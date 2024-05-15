import os
import json

#################
# Description   #
#################
# This script checks for existing posts (in the posts directory) for a given (JSON) hierarchy file.

#################
# Example       #
#################
# Existing posts:
# - Earth
# - The Nebular Hypothesis

# Missing posts:
# - Structure of the Sun
# - Solar Activity
# - Importance of the Sun
# - Mercury
# - Venus
# - Mars
# - Jupiter
# - Saturn
# - Uranus
# - Neptune
# - Pluto
# - Ceres
# - Eris
# - Makemake
# - Haumea
# - The Asteroid Belt
# - Composition of Asteroids
# - Notable Asteroids
# - Structure of Comets
# - Types of Comets
# - Famous Comets
# - Earth's Moon
# - The Galilean Moons
# - Other Notable Moons
# - Early Stages of the Solar System
# - Evolution of the Planets

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

def get_leaf_nodes(node):
    leaf_nodes = []
    if "subItems" in node:
        for sub_node in node["subItems"]:
            leaf_nodes.extend(get_leaf_nodes(sub_node))
    else:
        leaf_nodes.append(node)
    return leaf_nodes

def check_existing_posts(leaf_nodes, posts_dir):
    existing_posts = []
    missing_posts = []
    for node in leaf_nodes:
        post_name = node["href"].split("/")[-1]
        post_path = os.path.join(posts_dir, post_name + ".js")
        if os.path.exists(post_path):
            existing_posts.append(node)
        else:
            missing_posts.append(node)
    return existing_posts, missing_posts

if __name__ == "__main__":
    hierarchy_file = "../Transformer.codes/hierarchy/1.json"
    posts_dir = "../Transformer.codes/posts/"

    with open(hierarchy_file, "r") as f:
        hierarchy = json.load(f)

    leaf_nodes = get_leaf_nodes(hierarchy)

    existing_posts, missing_posts = check_existing_posts(leaf_nodes, posts_dir)

    print("Existing posts:")
    for post in existing_posts:
        print(f"- {post['name']}")

    print("\nMissing posts:")
    for post in missing_posts:
        print(f"- {post['name']}")
