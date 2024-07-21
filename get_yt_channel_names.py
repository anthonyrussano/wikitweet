import requests
import xml.etree.ElementTree as ET


def get_channel_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Find the channel title
        # The title is usually in the <title> tag within the <feed> tag
        title = root.find("{http://www.w3.org/2005/Atom}title").text
        return title
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"
    except AttributeError:
        return "Could not find channel title"


def main():
    input_file = "channel_urls.txt"  # Name of your input file
    output_file = "channel_titles.txt"  # Name of the output file

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            url = line.strip()
            title = get_channel_title(url)
            outfile.write(f"{url}: {title}\n")
            print(f"Processed: {url}")


if __name__ == "__main__":
    main()
