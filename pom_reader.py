from dataclasses import dataclass
import os
from pathlib import Path
from typing import List, Dict
import xml.etree.ElementTree as ET

DEPENDENCIES = 'dependencies'

JAR_INFO = 'jar_info'
VERSION = 'version'
PARENT = 'parent'
NAME = 'name'
JAR = 'jar'
POM = 'pom'
ARTIFACT_ID = 'artifact_id'
GROUP_ID = 'group_id'


GROUP_ID_STR_IN_POM = 'groupId'
ARTIFACT_ID_STR_IN_POM = 'artifactId'
PACKAGING_STR_IN_POM = 'packaging'

POM_NAMESPACE = "{http://maven.apache.org/POM/4.0.0}"

@dataclass
class Jar:
    def __init__(self,
                 name: str,
                 version: str,
                 parent: JAR = None,
                 dependency_jars: List[JAR] = None,
                 is_bom: bool = False):
        self.__name = name
        self.__version = version
        self.__parent = parent
        self.__dependency_jars = dependency_jars
        self.is_bom = is_bom


class PomReader:
    def read(self, project_path: str) -> List[str]:
        list_of_files = []
        for elem in Path(project_path).rglob('pom.xml'):
            if os.path.isfile(elem):
                list_of_files.append(elem)
            print(elem)
        return list_of_files

    def build_dep(self, list_of_pom_files: List) -> Dict:

        dependencies = []
        for file_name in list_of_pom_files:
            dependency_info = {}
            tree = ET.parse(file_name)
            root = tree.getroot()
            self.__get_dependencies(dependency_info=dependency_info, root=root, namespace=POM_NAMESPACE)
            self.__get_jar_properties(
                dependency_info=dependency_info,
                root=root,
                namespace=POM_NAMESPACE)
            self.__get_parent_properties(root=root, dependency_info=dependency_info,namespace=POM_NAMESPACE)
            dependencies.append(dependency_info)
        return dependencies

    def fill_inherited_data(self, dependencies: Dict):
        pass

    def __get_parent_properties(self, root, dependency_info: dict, namespace) -> Dict:
        parent = root.find(f'./{namespace}{PARENT}')
        parent_info = {}
        if parent is not None:
            artifact_id = parent.find(f'./{namespace}{ARTIFACT_ID_STR_IN_POM}').text
            version = parent.find(f'./{namespace}{VERSION}').text
            group_id = parent.find(f'./{namespace}{GROUP_ID_STR_IN_POM}').text
            parent_info[ARTIFACT_ID] = artifact_id
            parent_info[VERSION] = version
            parent_info[GROUP_ID] = group_id
            dependency_info[PARENT] = parent_info
        return dependency_info


    def __get_dependencies(self, dependency_info: Dict, root: ET.Element, namespace: str):
        info_list = []

        dependencies = root.find(f'{namespace}dependencies')
        for dependency in (dependencies or []):
            info = {}
            artifact_id = dependency.find(f'{namespace}{ARTIFACT_ID_STR_IN_POM}')
            version = dependency.find(f'{namespace}{VERSION}')
            group_id = dependency.find(f'{namespace}{GROUP_ID_STR_IN_POM}')
            scope = dependency.find(f'{namespace}scope')
            info[ARTIFACT_ID] = artifact_id.text

            if version is not None:
                info[VERSION] = version.text
                if info[VERSION].find('${') != -1:
                    target_version = version.text.replace('${', '').replace('}', '')
                    prop = root.find(f'./{namespace}properties')
                    if prop is not None:
                        version = prop.find(f'./{namespace}{target_version}')
                        if version is not None:
                            info[VERSION] = version.text
                        else:
                            info[VERSION] = 'inherited'
            info[GROUP_ID] = group_id.text
            if scope is not None:
                info['scope'] = scope.text

            info_list.append(info)

        dependency_info[DEPENDENCIES] = info_list

    def __get_jar_properties(self, dependency_info, root: ET.Element, namespace: str):
        jar_info = {}
        version = root.find(f'{namespace}{VERSION}')
        group_id = root.find(f'{namespace}{GROUP_ID_STR_IN_POM}')
        artifact_id = root.find(f'{namespace}{ARTIFACT_ID_STR_IN_POM}')
        packaging = root.find(f'{namespace}{PACKAGING_STR_IN_POM}')

        jar_info[ARTIFACT_ID] = artifact_id.text
        if version is not None:
            jar_info[VERSION] = version.text
        if group_id is not None:
            jar_info[GROUP_ID] = group_id.text
        if packaging is not None:
            jar_info[PACKAGING_STR_IN_POM] = packaging.text

        dependency_info[JAR_INFO] = jar_info

