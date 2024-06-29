import argparse
import logging
from typing import List

from orgparse.node import OrgNode
import orgparse

from aw_core.models import Event
from aw_client import ActivityWatchClient

def orgnode_to_event(node: OrgNode) -> List[Event]:
    events = []
    for cl in node.clock:
        data = dict(label=node.get_heading(), tags=list(node.tags))
        ts = cl.start # fix timezeon
        e = Event(timestamp=ts, duration=cl.duration, data=data)
        logging.debug("Event is mined: %s", e)
        events.append(e)
    return events

def load_orgfile(path: str):
    events = []
    root = orgparse.load(path)
    for node in root:
        if len(node.children) == 0:
            logging.debug("Handling heading: %s", node.get_heading())
            events += orgnode_to_event(node)
    return events


def main(args):
    files = [args.path]
    logging.info('Reading files: %s', files)


    bucket_name = 'org-mode-tracking'
    with ActivityWatchClient(testing=True) as aw:
        if bucket_name in aw.get_buckets():
            print(aw.get_events(bucket_name))
            aw.delete_bucket(bucket_name)

        aw.create_bucket(bucket_name, event_type="org-mode")

        for f in files:
            events = load_orgfile(f)
            print(events)
            aw.insert_events(bucket_name, events)
            print(aw.get_events(bucket_name))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    parser.add_argument('--log', type=str, default="ERROR")
    args = parser.parse_args()
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=args.log)


    main(args)
