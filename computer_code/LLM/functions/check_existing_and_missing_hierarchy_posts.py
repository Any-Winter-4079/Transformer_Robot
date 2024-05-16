import os
import json

#################
# Description   #
#################
# This script checks for the existance of posts for the leaf nodes in a hierarchy.

#################
# Sample result #
#################
# For 1.json:

# Existing posts:
# - Earth
# - The Nebular Hypothesis

# Missing posts:
# - Structure of the Sun
# - Solar Activity
# ...

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
HIERARCHIES_BASE_PATH = "../Transformer.codes/hierarchies/"
POSTS_DIR = "../Transformer.codes/posts/"

# Function to get leaf nodes from a hierarchy
def get_leaf_nodes(node):
    """Get leaf nodes from a hierarchy."""
    leaf_nodes = []
    if "subItems" in node:
        for sub_node in node["subItems"]:
            leaf_nodes.extend(get_leaf_nodes(sub_node))
    else:
        leaf_nodes.append(node)
    return leaf_nodes

# Function to check missing hierarchy posts
def check_existing_and_missing_hierarchy_posts(hierarchy_file_name):
    """Check existing and missing hierarchy posts."""

    with open(hierarchy_file_name, "r") as f:
        hierarchy = json.load(f)

    leaf_nodes = get_leaf_nodes(hierarchy)

    existing_posts = []
    missing_posts = []
    for node in leaf_nodes:
        post_name = node["href"].split("/")[-1]
        post_path = os.path.join(POSTS_DIR, post_name + ".js")
        if os.path.exists(post_path):
            existing_posts.append(node)
        else:
            missing_posts.append(node)

    print("Existing posts:")
    for post in existing_posts:
        print(f"- {post['name']}")

    print("\nMissing posts:")
    for post in missing_posts:
        print(f"- {post['name']}")

if __name__ == "__main__":
    hierarchy_path = f"{HIERARCHIES_BASE_PATH}/1.json"

    check_existing_and_missing_hierarchy_posts(hierarchy_path)
