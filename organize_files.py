"""Preview or copy files into extension folders. Python 3.10+, standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def plan(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_dir():
        raise ValueError('Source must be an existing directory')
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate, non-nested directories')
    if destination.exists():
        raise ValueError('Choose a new destination directory to prevent overwrites')
    entries = []
    for file in sorted(source.rglob('*')):
        if file.is_symlink() or (hasattr(file, 'is_junction') and file.is_junction()):
            raise ValueError('Links are not supported: ' + str(file))
        if not file.is_file():
            continue
        resolved = file.resolve()
        if source not in resolved.parents:
            raise ValueError('A file resolves outside the source directory')
        relative = file.relative_to(source)
        extension = file.suffix.lstrip('.').lower() or 'no-extension'
        # Keep the original relative path, so equal basenames never collide.
        target = destination / extension / relative
        entries.append({'source': str(file), 'target': str(target),
                        'bytes': file.stat().st_size,
                        'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    return {'source': str(source), 'destination': str(destination),
            'file_count': len(entries), 'files': entries}


def copy_files(manifest):
    # Rebuild the plan at execution time; callers cannot inject target paths.
    fresh = plan(manifest['source'], manifest['destination'])
    if fresh != manifest:
        raise ValueError('Source changed after preview; generate a new plan')
    destination = Path(manifest['destination'])
    destination.mkdir(parents=True, exist_ok=False)
    for entry in manifest['files']:
        target = Path(entry['target'])
        target.parent.mkdir(parents=True, exist_ok=True)
        with Path(entry['source']).open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Copy verification failed: ' + str(target))
    return manifest['file_count']


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--copy', action='store_true', help='Copy; default only prints a preview')
    args = parser.parse_args()
    try:
        manifest = plan(args.source, args.destination)
        if args.copy:
            copy_files(manifest)
        print(json.dumps({'mode': 'copied' if args.copy else 'preview', **manifest},
                         ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
