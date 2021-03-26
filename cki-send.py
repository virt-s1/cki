#!/usr/bin/python3

import argparse
import json
import stomp
import pathlib


def main(args):
    hosts = [
        ("messaging-devops-broker01.web.prod.ext.phx2.redhat.com", 61612),
        ("messaging-devops-broker02.web.prod.ext.phx2.redhat.com", 61612)
    ]
    conn = stomp.StompConnection12(host_and_ports=hosts,
                                   use_ssl=True,
                                   ssl_key_file=args.ssl_key_file,
                                   ssl_cert_file=args.ssl_cert_file)
    conn.connect(wait=True)

    msg = {
        "cki_pipeline_id": args.pipeline_id,
        "summarized_result": "PASS",
        "team_email": "3rd-qe-list@redhat.com",
        "team_name": "Virt-QE-S1",
        "results": []
    }

    template = {
        "test_name": "",
        "test_description": "Cloud platform - {}".format(args.cloud),
        "test_arch": "",
        "test_result": "",
        "test_log_url": [
            f"{args.build_url}display/redirect"
        ],
        "test_waived": "True"
    }

    running_path = pathlib.Path.cwd()
    print(running_path)

    files = running_path.glob('*.result')

    instances = [pathlib.PurePath(x).name.split(".")[:-1] for x in files]
    print(instances)

    for (x, y) in instances:
        filename = f"{x}.{y}.result"
        result = pathlib.Path(running_path / filename ).read_text().strip()
        new_temp = template.copy()
        new_temp["test_name"] = f"{args.cloud}-{x}"
        new_temp["test_description"] = f"Kernel test result on instance {x} of {args.cloud}"
        new_temp["test_arch"] = y
        new_temp["test_result"] = result
        msg["results"].append(new_temp)

    msg_json = json.dumps(msg)
    print(msg_json)
    conn.send("/topic/VirtualTopic.eng.cki.results",
              body=msg_json,
              headers={"topic": "VirtualTopic.eng.cki.results"})
    conn.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send result to VirtualTopic.eng.cki.results')
    parser.add_argument("--ssl_cert_file", type=str, required=True, help="Certification file")
    parser.add_argument("--ssl_key_file", type=str, required=True, help="Private key file")
    parser.add_argument("--pipeline_id", type=int, required=True, help="CKI pipeline ID")
    parser.add_argument("--build_url", type=str, required=True, help="Jenkins BUILD URL")
    parser.add_argument("--cloud", type=str, required=True, help="Cloud platform")
    args = parser.parse_args()

    main(args)
