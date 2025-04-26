python frame_splitter.py

### Watch Mode

You can run the script in watch mode to continuously monitor for new videos:
```
python frame_splitter.py -w
```
This will check for new videos every 60 seconds (configurable) and process them automatically.

### Options

- `-i, --input-dir`: Specify a custom input directory (default: "BeforeSplit")
- `-o, --output-dir`: Specify a custom output directory (default: "AfterSplit")
- `-d, --duration`: Specify segment duration (5-10 seconds)
- `-w, --watch`: Enable watch mode to continuously monitor for new videos
- `-t, --interval`: Seconds between checks in watch mode (default: 60)

### Examples

Process videos using custom directories:
```
python frame_splitter.py -i "MyVideos" -o "ProcessedVideos"
```

Watch a directory with 10-second segments:
```
python frame_splitter.py -d 10 -w
```

Watch with a shorter interval (30 seconds):
```
python frame_splitter.py -w -t 30
``` 