import argparse
import subprocess
import os
import time

MAX_TIMEOUT = 900  # 15 minutes in seconds
RED_COLOR = "\033[91m"
RESET_COLOR = "\033[0m"

def run_dirsearch_and_notify(url, wordlist_path, output_dir, automatic_skip=True):
    output_path = os.path.join(output_dir, f"{url.replace('://', '_').replace('/', '_')}_dirsearch.txt")
    dirsearch_command = [
        "dirsearch",
        "-u", url,
        "-w", wordlist_path,
        "-i", "200",
        "-o", output_path,
    ]

    try:
        start_time = time.time()
        subprocess.run(dirsearch_command, timeout=MAX_TIMEOUT, check=True)
        elapsed_time = time.time() - start_time
        print(f"Finished dirsearch for {url} in {elapsed_time:.2f} seconds")

        # After dirsearch completes, call the notify command with 'bug' as the ID and -data flag
        notify_command = ["notify", "-id", "bug", "-data", output_path]
        subprocess.run(notify_command, check=True)

    except subprocess.TimeoutExpired:
        print(f"Skipping {url} due to timeout")
        if not automatic_skip:
            should_skip = input("Do you want to skip this URL? (y/n): ")
            if should_skip.lower() == "y":
                print(f"Skipping {url}")
            else:
                print(f"Retrying dirsearch for {url}")
                run_dirsearch_and_notify(url, wordlist_path, output_dir, automatic_skip)
    except subprocess.CalledProcessError as e:
        print(f"Error running dirsearch for {url}: {e}")
        if not automatic_skip:
            should_skip = input("Do you want to skip this URL? (y/n): ")
            if should_skip.lower() == "y":
                print(f"Skipping {url}")
            else:
                print(f"Retrying dirsearch for {url}")
                run_dirsearch_and_notify(url, wordlist_path, output_dir, automatic_skip)

def main():
    parser = argparse.ArgumentParser(description="Automate dirsearch and notify for a list of URLs")
    parser.add_argument("--url-file", required=True, help="Path to the file containing URLs")
    parser.add_argument("--wordlist", required=True, help="Path to the wordlist file")
    parser.add_argument("--output-dir", required=True, help="Path to the output directory")
    parser.add_argument("--automatic-skip", action="store_true", help="Automatically skip URLs with timeouts or errors")
    args = parser.parse_args()

    with open(args.url_file, "r") as f:
        urls = f.read().splitlines()

    os.makedirs(args.output_dir, exist_ok=True)

    total_urls = len(urls)
    completed_urls = 0

    for url in urls:
        completed_urls += 1
        print(f"{RED_COLOR}Processing URL {completed_urls}/{total_urls}: {url}{RESET_COLOR}")
        run_dirsearch_and_notify(url, args.wordlist, args.output_dir, args.automatic_skip)
        print("=" * 50)

if __name__ == "__main__":
    main()
