import os

#################
# Description   #
#################
# This script discovers the first (non-existing) hierarchy file number.

#################
# Sample result #
#################
# The next hierarchy file to create is: 2.json

#################
# venv #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
HIERARCHIES_BASE_PATH = "../Transformer.codes/hierarchies/"

# Function to discover the next non-existing hierarchy file number
def discover_next_hierarchy():
    """Discover the next non-existing hierarchy file number."""
    i = 1
    while True:
        hierarchy_file_name = f"{i}.json"
        hierarchy_path = os.path.join(HIERARCHIES_BASE_PATH, hierarchy_file_name)
        if not os.path.exists(hierarchy_path):
            break
        i += 1
    print(f"The next hierarchy file to create is: {hierarchy_file_name}")

if __name__ == "__main__":
    discover_next_hierarchy()
