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

    running_path = pathlib.Path.cwd()
    print(running_path)

    reports = running_path.glob('*.report')

    msg = {
        "version": {
            "major": 4,
            "minor": 0
        },
        "tests": [],
    }
    for report in reports:
        # AWS instance types contain a .
        if args.cloud == "AWS-EC2":
            instance_type = ".".join(report.name.split(".")[:2])
        else:
            instance_type = report.name.split(".")[0]

        with report.open() as report_file:
            for line in report_file.readlines():
                test, status, _ = line.split()

                console_url = f"{args.build_url}artifact/output/{instance_type}-{test}.console"
                result_file_name = f'{instance_type}-{test}.result'
                result_url = f"{args.build_url}artifact/results/{result_file_name}"

                msg["tests"].append({
                    "build_id": args.kcidb_build_id,
                    "id": f'redhat:virt_qe_s1.{args.build_id}.{instance_type}.{test}',
                    "origin": "redhat",
                    "environment": {
                        "comment": f'Instance {instance_type} of {args.cloud}'
                    },
                    "path": f"ltp.{test}",
                    "log_url": console_url,
                    "status": status,
                    "waived": True,
                    "output_files": [
                        {
                            "name": "web_gui",
                            "url": f"{args.build_url}display/redirect",
                        },
                        {
                            "name": "consoleText",
                            "url": f"{args.build_url}consoleText",
                        },
                        {
                            "name": result_file_name,
                            "url": result_url,
                        },
                    ],
                })


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
    parser.add_argument("--kcidb_build_id", type=str, required=True, help="CKI KCIDB build_id of kernel tested")
    parser.add_argument("--build_url", type=str, required=True, help="Jenkins BUILD URL")
    parser.add_argument("--build_id", type=str, required=True, help="Jenkins BUILD ID")
    parser.add_argument("--cloud", type=str, required=True, help="Cloud platform")
    args = parser.parse_args()

    main(args)
