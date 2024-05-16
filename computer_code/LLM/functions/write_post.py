import os
import json

#################
# Description   #
#################
# This script writes the post content to a JavaScript file (exporting it in JSON format).

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Configuration #
#################
POSTS_DIR = "../Transformer.codes/posts/"

# Function to write the generated post content to a JavaScript file (exporting it in JSON format)
def write_post(file_name, post_content):
    """Write the generated post content to a JavaScript file (exporting it in JSON format)."""
    try:
        json.loads(post_content) # Validate the JSON
        file_path = os.path.join(POSTS_DIR, file_name)

        with open(file_path, 'w') as f:
            f.write(f"export default {post_content}")
        print(f"Post saved to {file_path}")

    except (json.JSONDecodeError, IOError) as e:
        print(f"Failed to save post: {str(e)}")

if __name__ == "__main__":
    file_name = "structure-of-the-sun.js"
    post_content = """
{
    "name": "Structure of the Sun",
    "id": 111,
    "sections": [
        {
            "h2": {
                "title": "Overview of the Sun's Structure"
            },
            "content": [
                {
                    "h3": {
                        "text": "Layers and Regions of the Sun"
                    }
                },
                {
                    "paragraph": [
                        {
                            "text": "The Sun, our closest star, has a complex internal structure consisting of several distinct layers. Understanding the Sun's structure is crucial for comprehending its behavior, energy production, and the phenomena observed on its surface and in the solar atmosphere."
                        }
                    ]
                },
                {
                    "paragraph": [
                        {
                            "text": "The Sun's structure is divided into two main regions: the"
                        },
                        {
                            "text": " interior",
                            "bold": true
                        },
                        {
                            "text": ", which includes the core, radiative zone, and convective zone; and the"
                        },
                        {
                            "text": " atmosphere",
                            "bold": true
                        },
                        {
                            "text": ", which consists of the photosphere, chromosphere, and corona."
                        }
                    ]
                }
            ]
        },
        {
            "h2": {
                "title": "The Sun's Interior"
            },
            "content": [
                {
                    "h3": {
                        "text": "Core, Radiative Zone, and Convective Zone"
                    }
                },
                {
                    "paragraph": [
                        {
                            "text": "At the heart of the Sun lies the core, where nuclear fusion reactions generate the Sun's energy. Surrounding the core is the radiative zone, where energy is transported outward by radiation. The outermost layer of the interior is the convective zone, where energy is transported by convection."
                        }
                    ]
                },
                {
                    "ul": [
                        {
                            "li": [
                                {
                                    "text": "The"
                                },
                                {
                                    "text": " core",
                                    "bold": true
                                },
                                {
                                    "text": " is the hottest and densest region, with temperatures reaching 15 million Kelvin."
                                }
                            ]
                        },
                        {
                            "li": [
                                {
                                    "text": "In the"
                                },
                                {
                                    "text": " radiative zone",
                                    "bold": true
                                },
                                {
                                    "text": ", energy is transported by photons that are repeatedly absorbed and re-emitted."
                                }
                            ]
                        },
                        {
                            "li": [
                                {
                                    "text": "The"
                                },
                                {
                                    "text": " convective zone",
                                    "bold": true
                                },
                                {
                                    "text": " is characterized by large-scale convective motions that transport energy to the surface."
                                }
                            ]
                        }
                    ]
                },
                {
                    "code": {
                        "text": "# Approximating the temperature gradient in the Sun's interior\\n\\nimport numpy as np\\n\\nr = np.linspace(0, 1, 100)  # Normalized radius (0 = center, 1 = surface)\\nT_core = 15e6  # Core temperature in Kelvin\\nT_surface = 5778  # Surface temperature in Kelvin\\n\\n# Temperature profile based on a simplified model\\nT = T_core * (1 - r**2) + T_surface * r**2\\n\\nprint(f\\"The temperature at the Sun's surface is approximately {T[-1]:.0f} Kelvin.\\")",
                        "language": "python"
                    }
                },
                {
                    "paragraph": [
                        {
                            "text": "This simplified model shows the temperature gradient from the core to the surface, with the surface temperature around 5778 Kelvin."
                        }
                    ]
                }
            ]
        },
        {
            "h2": {
                "title": "The Sun's Atmosphere"
            },
            "content": [
                {
                    "h3": {
                        "text": "Photosphere, Chromosphere, and Corona"
                    }
                },
                {
                    "paragraph": [
                        {
                            "text": "The Sun's atmosphere consists of three main layers: the photosphere, chromosphere, and corona. Each layer has distinct characteristics and plays a role in solar phenomena."
                        }
                    ]
                },
                {
                    "ul": [
                        {
                            "li": [
                                {
                                    "text": "The"
                                },
                                {
                                    "text": " photosphere",
                                    "bold": true
                                },
                                {
                                    "text": " is the visible surface of the Sun, emitting most of the Sun's light."
                                }
                            ]
                        },
                        {
                            "li": [
                                {
                                    "text": "The"
                                },
                                {
                                    "text": " chromosphere",
                                    "bold": true
                                },
                                {
                                    "text": " is a thin, reddish layer above the photosphere, visible during solar eclipses."
                                }
                            ]
                        },
                        {
                            "li": [
                                {
                                    "text": "The"
                                },
                                {
                                    "text": " corona",
                                    "link": "https://example.com/corona"
                                },
                                {
                                    "text": " is the outermost layer, extending millions of kilometers into space."
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "h2": {
                "title": "Importance of the Sun's Structure"
            },
            "content": [
                {
                    "h3": {
                        "text": "Understanding Solar Dynamics and Activity"
                    }
                },
                {
                    "paragraph": [
                        {
                            "text": "Studying the Sun's structure is essential for understanding solar dynamics, energy production, and the impact of solar activity on Earth. By exploring the Sun's interior and atmosphere, we gain insights into the fundamental processes governing our nearest star and its far-reaching influences."
                        }
                    ]
                }
            ]
        }
    ]
}
"""
    write_post(file_name, post_content)
