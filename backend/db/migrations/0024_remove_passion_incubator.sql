-- Passion Incubator removal cleanup — renames shared infrastructure that
-- other active features (Decision Lab, Knowledge Circles) still use, so
-- nothing is misleadingly named after a deleted feature. A rename (not a
-- drop+recreate) preserves every seeded resource-domain row and every
-- real Knowledge Circle link with zero data loss.

alter table if exists passion_resource_domains rename to topic_resource_domains;
alter table if exists knowledge_circles rename column linked_passion_domain_ids to linked_topic_domain_ids;
