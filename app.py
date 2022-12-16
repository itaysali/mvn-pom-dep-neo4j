"""This code demonstrates creation of nodes and relationship between those: create_sample_data. And then it
demonstrates some sample queries, using both techniques provided by neomodel and cypher query: Refer  sample_queries
"""
from neomodel import db, Q

from pom_graph_builder import PomGraphBuilder
from pom_reader import PomReader

PROJECT_PATH = '/home'

def create_dependencies():
    global pom_reader, pom_graph_builder, dependencies
    pom_reader = PomReader()
    pom_graph_builder = PomGraphBuilder()
    file_list = pom_reader.read(PROJECT_PATH)
    dependencies = pom_reader.build_dep(list_of_pom_files=file_list)
    pom_graph_builder.build_graph(dependency_info=dependencies)


if __name__ == '__main__':

    delete:bool = True
    generate_graph: bool = True
    if delete:
        # delete existing data prior to loading
        results, meta = db.cypher_query("MATCH (s:SoftwareLibrary) DETACH DELETE (s)")
        results, meta = db.cypher_query("MATCH (l:LibraryRel) DETACH DELETE (l)")
        results, meta = db.cypher_query("MATCH (l:ArtifactSoftwareLibrary) DETACH DELETE (l)")
        results, meta = db.cypher_query("MATCH (l:ParentSoftwareLibrary) DETACH DELETE (l)")
        results, meta = db.cypher_query("MATCH (l:PomSoftwareLibrary) DETACH DELETE (l)")

    if generate_graph:
        create_dependencies()

