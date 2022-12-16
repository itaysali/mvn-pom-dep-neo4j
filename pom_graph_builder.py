from model import SoftwareLibrary, ArtifactSoftwareLibrary, PomSoftwareLibrary, ParentSoftwareLibrary
from pom_reader import JAR, POM, JAR_INFO, PARENT, VERSION, DEPENDENCIES, ARTIFACT_ID, GROUP_ID, NAME


class PomGraphBuilder:
    def build_graph(self, dependency_info: dict):
        print(dependency_info)
        for library_info in dependency_info:
            jar_library = self.__build_jar(library_info=library_info)
            self.__build_parent(library_info=library_info, jar_library=jar_library)
            self.__build_dependencies(
                library_info=library_info,
                jar_library=jar_library)

    def __build_jar(self, library_info: dict) -> SoftwareLibrary:
        jar_info = library_info[JAR_INFO]
        name = None
        group_id = None
        version = None
        packaging = None
        if jar_info.get(NAME) is not None:
            name = jar_info[NAME]
        if jar_info.get(VERSION) is not None:
            version = jar_info[VERSION]
        artifact_id = jar_info[ARTIFACT_ID]
        if jar_info.get(GROUP_ID) is not None:
            group_id = jar_info[GROUP_ID]
        if jar_info.get('packaging') is not None:
            packaging = jar_info['packaging']
        jar_library = None

        if packaging is None and packaging != POM:
            jar_library = SoftwareLibrary(
                name=name,
                version=version,
                artifact_id=artifact_id,
                group_id=group_id,
                packaging=packaging).save()
        else:
            jar_library = PomSoftwareLibrary(
                name=name,
                version=version,
                artifact_id=artifact_id,
                group_id=group_id,
                packaging=packaging).save()

        artifact = ArtifactSoftwareLibrary.nodes.get_or_none(artifact_id=artifact_id)
        if artifact is None:
            artifact = ArtifactSoftwareLibrary(artifact_id=artifact_id).save()

        jar_library.artifact.connect(artifact, {'relationship_type': 'artifact'})
        jar_library.save()

        return jar_library

    def __build_dependencies(self, library_info, jar_library: dict):
        for dep_library in library_info[DEPENDENCIES]:
            dep_artifact_id = dep_library.get(ARTIFACT_ID)
            dep_group_id = dep_library.get(GROUP_ID)
            dep_version = dep_library.get(VERSION)
            dep_name = dep_library.get('name')
            dep_software_library = self.get_node(
                artifact_id=dep_artifact_id,
                group_id=dep_group_id,
                version=dep_version)

            if dep_software_library is None:
                dep_software_library = SoftwareLibrary(
                    artifact_id=dep_artifact_id,
                    name=dep_name)

                if dep_library.get(NAME) is not None:
                    dep_name = dep_library[NAME]
                    dep_software_library.name = dep_name

                if dep_library.get(GROUP_ID) is not None:
                    group_id = dep_library[GROUP_ID]
                    dep_software_library.group_id = group_id

                if dep_library.get(VERSION) is not None:
                    dep_version = dep_library[VERSION]
                    dep_software_library.version = dep_version
            dep_software_library.save()
            jar_library.artifact_dependencies.connect(dep_software_library, {'relationship_type': 'dependency'})
            jar_library.save()

    def __find_parent_dependencies(self, parent_info: dict, dependency_info: dict) -> dict:
        for dep in dependency_info:
            if dep[JAR_INFO][ARTIFACT_ID] == parent_info[ARTIFACT_ID] and dep[JAR_INFO][VERSION] == parent_info[VERSION]:
                return dep



    def __build_parent(self,
                       jar_library: dict,
                       library_info: dict) -> ParentSoftwareLibrary:

        parent = library_info.get(PARENT)
        parent_library = None
        if parent is not None:
            version = parent[VERSION]
            artifact_id = parent[ARTIFACT_ID]
            group_id = parent[GROUP_ID]
            parent_library = ParentSoftwareLibrary.nodes.get_or_none(
                version=version,
                artifact_id=artifact_id,
                group_id=group_id)
            if parent_library is None:
                parent_library = ParentSoftwareLibrary(
                    version=version,
                    artifact_id=artifact_id,
                    group_id=group_id).save()
            jar_library.parent.connect(parent_library, {'relationship_type': 'parent'})
            jar_library.save()
        return parent_library

    def get_node(
            self,
            artifact_id: str,
            group_id: str,
            version: str):
        library = None
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=version, artifact_id=artifact_id, packaging=JAR,
                                                        group_id=group_id)
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=version, artifact_id=artifact_id, packaging=JAR)
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=version, artifact_id=artifact_id, group_id=group_id)
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=version, artifact_id=artifact_id)
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=None, artifact_id=artifact_id, packaging=JAR)
        if library is None:
            library = SoftwareLibrary.nodes.get_or_none(version=None, artifact_id=artifact_id)
        return library
