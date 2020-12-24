# CKI - Continuous Kernel Integration

Onboard Cloud CI system to take advantage of testing CKI kernels, which includes targeted testing for patches, upstream kernels, or official builds.

### Download CKI kernel

    ansible-playbook -v -i inventory -e cki_repo_url=<cki repo url> download.yaml

### Install kernel

    ansible-playbook -v -i inventory install.yaml

### Run LTP test

    ansible-playbook -v -i inventory run-ltp.yaml

### Send result on UMB

    ansible-playbook -v -i inventory -e cloud_platform=esxi/aws/openstack umb.yaml

### Add target VM IP address from kite-deploy repo to this repo

    ansible-playbook -v -i inventory setup.yaml

## Configuration

You can set these environment variables to configure to run test

    TEST_OS         The OS to run the tests in.  Currently supported values:
                        "rhel-8-3"
                        "rhel-8-4"

    VSPHERE_SERVER  The vSphere server hostname or IP address

    VSPHERE_USERNAME  Username to login vSphere server

    VSPHERE_PASSWORD  Password to login vSphere server

    ESXI_HOST         ESXi host name or IP address
