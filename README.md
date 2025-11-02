# Automate Node.js Deployment with Ansible (AWS + Linux)

This sample project shows a complete, opinionated way to deploy a simple Node.js application to an AWS EC2 Linux server using Ansible.

What you get in this repo:
- Ansible playbooks to provision (optionally) an EC2 instance and to provision & deploy the Node.js app
- A small sample Node.js app (server.js + package.json)
- An Ansible role `nodeapp` that installs Node.js, creates an app user, clones your app, and runs it as a systemd service
- Templates and example inventory/configuration

High-level workflow:
1. Prepare environment (install Ansible, Python deps, and Ansible collections)
2. (Optional) Launch an EC2 instance using the included playbook
3. Update inventory.ini with your instance's public IP (or use the create_ec2 playbook's auto-added host)
4. Run the deployment playbook to provision OS packages, create the app user, clone the repo, install dependencies, and start the Node.js app as a systemd service

Prerequisites
- Ansible 2.10+ (collections-based)
- Python 3 and pip
- boto3, botocore (if using the create_ec2 playbook)
- Ansible collections: amazon.aws (for create_ec2), community.general (if needed)
- AWS credentials configured (environment variables or `~/.aws/credentials`)
- An SSH key pair that can access the EC2 instance and the private key path locally
- (Optional) A public AMI ID for your region (Ubuntu 20.04 or Amazon Linux)

Folder layout
- ansible.cfg
- inventory.ini
- playbooks/create_ec2.yml      # optional: create EC2 instance using amazon.aws.ec2_instance
- playbooks/deploy.yml         # main playbook to provision & deploy
- roles/nodeapp/
  - tasks/main.yml
  - vars/main.yml
  - templates/nodeapp.service.j2
- app/
  - server.js
  - package.json
- .gitignore

How to use (step-by-step)
1. Install prerequisites:
   - pip install --user ansible boto3 botocore
   - ansible-galaxy collection install amazon.aws
2. Clone this repo locally (or create it from these files)
3. Edit `roles/nodeapp/vars/main.yml` and set `nodeapp_repo` to your repo URL after you upload this project to GitHub. You may leave it pointing to the sample app included here (it defaults to a placeholder).
4. Option A — Launch an EC2 instance automatically:
   - Edit `playbooks/create_ec2.yml` variables (AMI image_id, key_name, region, security_group)
   - Run:
     ansible-playbook playbooks/create_ec2.yml
   - That playbook will register the new instance and add it to the `appservers` group in memory so you can immediately run the deploy playbook.
5. Option B — Create an EC2 instance manually:
   - Create an EC2 instance (Ubuntu server recommended), open port 22 and port 3000 in the security group
   - Put the instance's public IP into `inventory.ini` under the `[appservers]` group and set `ansible_user` to the distro user (e.g., `ubuntu` for Ubuntu AMIs)
6. Deploy the Node.js app:
   - Run:
     ansible-playbook -i inventory.ini playbooks/deploy.yml --private-key /path/to/your/key.pem
   - The playbook will:
     - install Node.js and git
     - create the `nodeapp` user
     - clone the application repo (or use the sample included repo URL)
     - install npm dependencies
     - create and enable a systemd service to manage the app
7. Verify:
   - Visit http://<EC2_PUBLIC_IP>:3000 and you should see "Hello from Node.js!" (sample app)

Notes and tips
- The `create_ec2.yml` playbook uses the `amazon.aws.ec2_instance` module. It requires the `amazon.aws` Ansible collection and boto3.
- Replace placeholders like `ami-xxxxxxxx`, `your-key-name`, `your-security-group` with values that match your AWS account.
- If you plan to deploy from the GitHub repo, set `nodeapp_repo` in `roles/nodeapp/vars/main.yml` to the raw HTTPS clone URL for your repository (e.g., https://github.com/<you>/<repo>.git).

Security
- Do not hardcode AWS secret keys in files. Use environment variables or standard AWS credential mechanisms.
- Limit security group rules to trusted IPs.