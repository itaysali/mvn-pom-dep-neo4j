"""This code defines the object structures for Team Member, Skill, and the relationship between those two. Use the
following commands to create these definitions in neo4j.
    neomodel_install_labels --db bolt://neo4j:password@localhost:7687 model.py
"""

from neomodel import (config, StructuredNode, StringProperty, Relationship, ZeroOrMore,
                      StructuredRel)

config.DATABASE_URL = "bolt://neo4j:password@localhost:7687"

class LibraryRel(StructuredRel):
    relationship_type = StringProperty(required=True)


class SoftwareLibrary(StructuredNode):
    name = StringProperty(required=False)
    group_id = StringProperty(required=False)
    full_name = StringProperty(required=False)
    version = StringProperty(required=False)
    scope = StringProperty(required=False)
    artifact_id = StringProperty(required=True)
    packaging = StringProperty(required=False)

    artifact_dependencies = Relationship('SoftwareLibrary', 'DEPENDENT_ON', cardinality=ZeroOrMore, model=LibraryRel)
    parent = Relationship('ParentSoftwareLibrary', 'INHERIT_FROM_PARENT', cardinality=ZeroOrMore, model=LibraryRel)
    artifact = Relationship('ArtifactSoftwareLibrary', 'ARTIFACT_DEPENDENT_ON', cardinality=ZeroOrMore, model=LibraryRel)

class ArtifactSoftwareLibrary(SoftwareLibrary):
    pass

class ParentSoftwareLibrary(SoftwareLibrary):
    pass

class PomSoftwareLibrary(SoftwareLibrary):
    pass

