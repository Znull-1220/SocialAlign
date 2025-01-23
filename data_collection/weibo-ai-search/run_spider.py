import subprocess
import os
import argparse

def run_spider(url, output_file):
    # change the current working directory to the directory of this script
    target_dir = os.path.dirname(__file__)
    os.chdir(target_dir)

    command = [
        "scrapy", "crawl", "weibo", 
        "-a", f"url={url}",
        "-o", output_file
    ]
    subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='execute spider for Weibo AI Search')
    parser.add_argument('--url', type=str, required=True, help='The URL to be crawled')
    parser.add_argument('--output', type=str, default='./crawled_data/topic_name.json',
                      help='output file path (default: ./crawled_data/topic_name.json)')
    
    args = parser.parse_args()
    run_spider(args.url, args.output)