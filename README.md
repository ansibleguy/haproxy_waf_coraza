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
  apps:
    - name: 'default'
      block: false

    - name: 'default_block'
      block: true

    - name: 'be_app1'
      block: true
```

Then you will need to include the SPOE-backend: `/etc/haproxy/waf-coraza.cfg`

And target the SPOE-agents in your HAProxy config:

`filter spoe engine coraza_waf_<APP-NAME> config /etc/haproxy/waf-coraza.cfg if <YOUR-CONDITION>`

### Result

**Config-Directory**:
```bash
tree /etc/coraza-spoa -L 4
> /etc/coraza-spoa
> ├── apps
> │   ├── be_app1
> │   │   └── v4.7.0
> │   │       ├── @crs-setup.conf
> │   │       ├── main.conf
> │   │       └── @owasp_crs
> │   ├── default
> │   │   └── v4.7.0
> │   │       ├── @crs-setup.conf
> │   │       ├── main.conf
> │   │       └── @owasp_crs
> │   ├── default_block
> │   │   └── v4.7.0
> │   │       ├── @crs-setup.conf
> │   │       ├── main.conf
> │   │       └── @owasp_crs
> │   └── _tmpl
> │       └── v4.7.0
> │           └── ...
> └── spoa.yml

# haproxy spoe backend: /etc/haproxy/waf-coraza.cfg
# haproxy spoe agents: /etc/haproxy/waf-coraza-spoe.cfg

cat /etc/haproxy/waf-coraza-spoe.cfg 
> # Ansible managed
> # ansibleguy.haproxy_waf_coraza
> 
> [coraza_waf_default]
> spoe-agent coraza_waf_default_agent
>     messages    coraza_waf_default_req
>     option      var-prefix      coraza
>     option      set-on-error    error
>     timeout     hello           2s
>     timeout     idle            2m
>     timeout     processing      500ms
>     use-backend coraza-waf-spoa
>     log         global
> 
> spoe-message coraza_waf_default_req
>     args app=str(default) src-ip=src src-port=src_port dst-ip=dst dst-port=dst_port method=method path=path query=query version=req.ver headers=req.hdrs body=req.body
>     event on-frontend-http-request
> 
> 
> [coraza_waf_default_block]
> ...
```


----

## Functionality

* **Package installation**
  * Downloading WAF-Binary
  * Rsyslog & Logrotate if `log.syslog` is enabled

* **Configuration**

  * **Default config**:
    * WAF Configuration at: `/etc/coraza-spoa`
      * Application-Specific rulesets: `/etc/coraza-spoa/apps/<app>/<version>/`
      * [Coraza Core-Ruleset](https://github.com/corazawaf/coraza-coreruleset)
      * [Easy-to-manage Config](https://coraza.io/docs/seclang/directives/)
      * App-specific rule-overrides
    * App-Specific Log-File at `/var/log/coraza-spoa`
      * Log-File => Syslog with App-Specific Tags


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


* **Info:** You need to configure the WAF-Applications yourself if HAProxy is not managed by the [ansibleguy/infra_haproxy]() Ansible-role!

  You can do so by adding this line to the config:

  ```
  filter spoe engine coraza_waf_<APP-NAME> config /etc/haproxy/waf-coraza.cfg if <YOUR-CONDITION>
  ```


----

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

There are also some useful **tags** available:
* install
* logs
* apps => add or update an app
* config => only update config
* rules => only update rules

To debug errors - you can set the 'debug' variable at runtime:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e debug=yes
```
