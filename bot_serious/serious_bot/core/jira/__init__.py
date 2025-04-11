import re
import json
import xml.etree.ElementTree as ET
from packaging.version import Version

import requests
from jira import JIRA

from loguru import logger


GET_FOREST_RESOURCE_API_END = "rest/structure/2.0/forest/latest"
GET_VALUE_RESOURCE_API_END = "rest/structure/2.0/value"


class JiraClient:
    def __init__(self, base_url, token, logger):
        self.logger = logger
        self.base_url = base_url
        self.token = token
        self.jira = JIRA(token_auth=token, server=base_url)

    def search_issues(self, filter_id: str, fields: []) -> []:
        search_result = self.jira.search_issues(
            f'filter={filter_id}',
            validate_query=False,
            fields=fields
        )
        return search_result

    def parse_structure_get_latest_release_candidate(
            self, structure_id, base_version, platform, product: str = 'VK Teams On-Premise',
    ):
        # получим элементы структуры в raw формате
        forrest_formula = self._get_structure_as_forest(structure_id)
        # распарсим эти элементы в более простой формат
        parsed_forest_elements = self._parse_formula_elements(formula=forrest_formula)
        # получим названия этих элементов в структуре, то есть их summary
        parsed_forest_elements_summary_map = self._get_value_resource_of_depth_0_from_structure_forest(
            structure_id, parsed_forest_elements
        )
        # отберём из них только те, что являются дочерними в папке Активные
        row_ids_of_target_issues = self._get_row_ids_of_issues_from_active_releases_folder(
            parsed_forest_elements, parsed_forest_elements_summary_map
        )
        # получим словарь только тех дочерних элементов, что являются Jira-тасками релиз-кандидатов VK Teams
        target_summary_by_issue_id_map = self._get_summary_by_issue_id_dict_for_specified_string(
            structure_id, parsed_forest_elements, row_ids_of_target_issues, product,
        )

        # получим искомую по платформе, продукту и версии последний активный релиз-кандидат
        latest_version = None
        latest_release_name = None
        latest_release_issue_id = None
        latest_release_version = None
        latest_rc_number = -1

        for issue_id, release in target_summary_by_issue_id_map.items():
            if product in release and platform in release:
                # Извлекаем версию и RC из строки
                match = re.search(r'(\d+(\.\d+)*)(?: RC(\d+))?', release)
                if match:
                    version_str = match.group(1)
                    rc_number = int(match.group(3)) if match.group(3) else 0

                    if base_version and not version_str.startswith(base_version):
                        continue

                    try:
                        version = Version(version_str)
                        if (latest_version is None or
                                version > latest_version or
                                (version == latest_version and rc_number > latest_rc_number)):
                            latest_version = version
                            latest_rc_number = rc_number
                            latest_release_name = release
                            latest_release_issue_id = issue_id
                            latest_release_version = version_str
                    except ValueError:
                        continue  # Пропускаем некорректные версии

        if latest_release_name and latest_release_issue_id and latest_release_version:
            jira_issue = self.jira.issue(latest_release_issue_id)
            status = jira_issue.fields.status.name
            issue_key = jira_issue.key
            return latest_release_name, status, issue_key, latest_release_version

        return None, None, None, None

    def _get_structure_as_forest(self, structure_id):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        params = {
            's': json.dumps({'structureId': structure_id})
        }

        response = requests.get(f"{self.base_url}/{GET_FOREST_RESOURCE_API_END}", params=params, headers=headers)
        forest_data = response.json()

        return forest_data.get("formula", "")

    def _parse_formula_elements(self, formula):
        elements = formula.split(',')
        parsed_elements = []
        for element in elements:
            parts = element.split(':')
            if len(parts) == 3:
                row_id, depth, issue_id = parts
                parsed_elements.append({
                    'row_id': int(row_id),
                    'depth': int(depth),
                    'issue_id': issue_id,
                    'item_type': 0
                })
            elif len(parts) == 4:
                row_id, depth, issue_id, item_type = parts
                parsed_elements.append({
                    'row_id': int(row_id),
                    'depth': int(depth),
                    'issue_id': issue_id,
                    'item_type': int(item_type)
                })
        return parsed_elements

    def _get_value_resource_of_depth_0_from_structure_forest(self, structure_id, parsed_elements):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        depth_0_rows = [el['row_id'] for el in parsed_elements if el['depth'] == 0]
        value_request = {
            "requests": [
                {
                    "forestSpec": {
                        "structureId": structure_id
                    },
                    "rows": depth_0_rows,
                    "attributes": [
                        {
                            "id": "summary",
                            "format": "text"
                        }
                    ]
                }
            ]
        }

        response = requests.post(f"{self.base_url}/{GET_VALUE_RESOURCE_API_END}", headers=headers, json=value_request)
        root = ET.fromstring(response.content)

        summary_map = {}
        rows = root.findall('.//rows')
        values = root.findall('.//values')

        for row_elem, value_elem in zip(rows, values):
            row_id = int(row_elem.text)
            summary = value_elem.text
            summary_map[row_id] = summary

        return summary_map

    def _get_row_ids_of_issues_from_active_releases_folder(self, parsed_elements, summary_map):
        active_row_ids = set()
        parent_stack = []

        for element in parsed_elements:
            if element['depth'] == 0:
                parent_stack = [element]
            else:
                while parent_stack and parent_stack[-1]['depth'] >= element['depth']:
                    parent_stack.pop()

                parent_stack.append(element)

            if parent_stack[0]['depth'] == 0 and summary_map.get(parent_stack[0]['row_id']) == "Активные":
                if element['item_type'] in [3, 4]:
                    active_row_ids.add(element['row_id'])

        return active_row_ids

    def _get_summary_by_issue_id_dict_for_specified_string(
            self, structure_id, parsed_elements, active_issue_ids, target_string: str = 'VK Teams'
    ):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        value_request = {
            "requests": [
                {
                    "forestSpec": {
                        "structureId": structure_id
                    },
                    "rows": list(active_issue_ids),
                    "attributes": [
                        {
                            "id": "summary",
                            "format": "text"
                        }
                    ]
                }
            ]
        }

        response = requests.post(f"{self.base_url}/{GET_VALUE_RESOURCE_API_END}", headers=headers, json=value_request)
        root = ET.fromstring(response.content)

        issue_summaries = {}
        rows = root.findall('.//rows')
        values = root.findall('.//values')

        for row_elem, value_elem in zip(rows, values):
            row_id = int(row_elem.text)
            summary = value_elem.text
            issue_summaries[row_id] = summary

        summary_by_issue_id = {}
        for el in parsed_elements:
            if el['row_id'] in active_issue_ids:
                row_id = el['row_id']
                summary = issue_summaries.get(row_id, "No summary found")
                if target_string in summary:
                    logger.info(f"summary: {summary}")
                    logger.info(f"el['issue_id']: {el['issue_id']}")
                    logger.info(f"el['row_id']: {el['row_id']}")
                    summary_by_issue_id[el['issue_id']] = summary

        return summary_by_issue_id
