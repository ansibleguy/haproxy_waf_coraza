<a href="https://coraza.io/">
<img src="https://owasp.org/www-project-developer-guide/assets/images/logos/coraza.png" alt="Coraza WAF Logo" width="600"/>
</a>

# Ansible Role - Coraza WAF HAProxy Integration (SPOA)

Role to deploy the [Coraza WAF HAProxy SPOA-integration](https://github.com/corazawaf/coraza-spoa) with its [Core-Ruleset](https://github.com/corazawaf/coraza-coreruleset).

We focus on the HAProxy community-edition as the enterprise-edition already has a built-in WAF!

<a href='https://ko-fi.com/ansible0guy' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy me a coffee' />

**Tested:**
* Debian 12

----

## Install

```bash
# latest
ansible-galaxy role install git+https://github.com/ansibleguy/haproxy_waf_coraza

# from galaxy
ansible-galaxy install ansibleguy.haproxy_waf_coraza

# or to custom role-path
ansible-galaxy install ansibleguy.haproxy_waf_coraza --roles-path ./roles
```

----

## Advertisement

* Need **professional support** using Ansible, HAProxy or the Coraza WAF? Contact us:

  E-Mail: [contact@oxl.at](mailto:contact@oxl.at)

  Tel: [+43 3115 40 900 0](tel:+433115409000)

  Web: [EN](https://www.o-x-l.com) | [DE](https://www.oxl.at)

  Language: German or English

* You want a simple **Ansible GUI**?

  Check-out this [Ansible WebUI](https://github.com/ansibleguy/webui)

----


## Usage

### Config

**Minimal example**

```yaml
waf:
  ...
```

----

Define the config as needed:

```yaml
waf:
  ...
```

You might want to use 'ansible-vault' to encrypt your passwords:
```bash
ansible-vault encrypt_string
```

----

## Functionality

* **Package installation**
  * Downloading WAF-Binary

* **Configuration**

  * **Default config**:
    * ...


  * **Default opt-ins**:
    * ...


  * **Default opt-outs**:
    * ...

----

## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of the role's functionality can be opted in or out.

  For all available options - see the default-config located in [the main defaults-file](https://github.com/ansibleguy/infra_haproxy/blob/latest/defaults/main/1_main.yml)!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Info:** ...


----

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

To debug errors - you can set the 'debug' variable at runtime:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e debug=yes
```
