<a href="https://coraza.io/">
<img src="https://owasp.org/www-project-developer-guide/assets/images/logos/coraza.png" alt="Coraza WAF Logo" width="600"/>
</a>

# Ansible Role - Coraza WAF HAProxy Integration (SPOA)

Role to deploy the [Coraza WAF (OWASP)](https://coraza.io/) [HAProxy SPOA-integration](https://github.com/corazawaf/coraza-spoa) with its [Core-Ruleset](https://github.com/corazawaf/coraza-coreruleset).

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

### Example

Here some detailed config example and its results:

* [Example](https://github.com/ansibleguy/haproxy_waf_coraza/blob/latest/Example.md)

### Config

**Example**

```yaml
waf:
  apps:
    - name: 'default'
      block: false

    - name: 'default_block'
      block: true

    - name: 'be_app1'
      block: true

      rules:
        # override vars inside CoreRuleset config REQUEST-901-INITIALIZATION.conf
        vars:
          tx.allowed_methods: 'GET HEAD POST PUT OPTIONS'

        rule_changes:
          # disable PHP-checks
          'REQUEST-933-APPLICATION-ATTACK-PHP.conf': false

          # re-enable it
          # 'REQUEST-933-APPLICATION-ATTACK-PHP.conf': true

          # change/update single rules
          'REQUEST-944-APPLICATION-ATTACK-JAVA.conf':
            # disable (comment-out) single rule
            944100: false

            # re-enable it
            # 944100: true
                        
            # replace a rule with custom content
            944140: |
              SecRule ... \
                  "id:944140, ..."

```

----

### HAProxy Integration

Then you will need to include the SPOE-backend: `/etc/haproxy/waf-coraza.cfg`

And target the SPOE-agents in your HAProxy config: (or use the role [ansibleguy/infra_haproxy](https://github.com/ansibleguy/infra_haproxy) with `haproxy.waf.coraza.enable=true`)

```
http-request set-var(txn.waf_app) str(app1) if { req.hdr(host) -i -m str ansibleguy.net test.ansibleguy.net }

# fallback app
http-request set-var(txn.waf_app) str(default) if !{ var(txn.waf_app) -m found }

filter spoe engine coraza config /etc/haproxy/waf-coraza-spoe.cfg
http-request send-spoe-group coraza coraza-req
```

To log related information in HAProxy: (*after the send-spoe-group line*)

```
http-request capture var(txn.waf_app) len 50
http-request capture var(txn.coraza.id) len 16
http-request capture var(txn.coraza.error) len 1
http-request capture var(txn.coraza.action) len 8
```

And then perform the result-actions:

```
# deny or silent-drop:
http-request deny status 403 if { var(txn.coraza.action) -m str deny }
http-response deny status 403 if { var(txn.coraza.action) -m str deny }

http-request silent-drop if { var(txn.coraza.action) -m str drop }
http-response silent-drop if { var(txn.coraza.action) -m str drop }

# optional - redirect:
http-request redirect code 302 location %[var(txn.coraza.data)] if { var(txn.coraza.action) -m str redirect }
http-response redirect code 302 location %[var(txn.coraza.data)] if { var(txn.coraza.action) -m str redirect }
```

----

### Result

```bash
tree /etc/coraza-spoa -L 4
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
> [coraza]
> spoe-agent coraza-agent
>     messages    coraza-req
>     option      var-prefix      coraza
>     option      set-on-error    error
>     timeout     hello           2s
>     timeout     idle            2m
>     timeout     processing      500ms
>     use-backend coraza-waf-spoa
>     log         global
> 
> spoe-message coraza-req
>     args app=var(txn.waf_app) src-ip=src src-port=src_port dst-ip=dst dst-port=dst_port method=method path=path query=query version=req.ver headers=req.hdrs body=req.body
>     event on-backend-http-request

cat /etc/coraza-spoa/spoa.yml 
> ---
> bind: '127.0.0.1:9000'
> 
> log_file: '/dev/stdout'
> log_level: 'info'
> log_format: 'json'
> 
> applications:
>   - name: 'default'
>     directives: |
>       Include /etc/coraza-spoa/apps/default/v4.7.0/main.conf
>       Include /etc/coraza-spoa/apps/default/v4.7.0/@crs-setup.conf
>       Include /etc/coraza-spoa/apps/default/v4.7.0/@owasp_crs/*.conf
> 
>     response_check: false
>     transaction_ttl_ms: 60000
> 
>     log_level: 'info'
>     log_file: '/var/log/coraza-spoa/default.log'
>     log_format: 'json'
>
>   ...
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

  For all available options - see the default-config located in [the main defaults-file](https://github.com/ansibleguy/haproxy_waf_coraza/blob/latest/defaults/main/1_main.yml)!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Info:** You need to configure the WAF-Applications yourself if HAProxy is not managed by the [ansibleguy/infra_haproxy](https://github.com/ansibleguy/infra_haproxy) Ansible-role (after setting `haproxy.waf.coraza.enable=true`)!


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

You can also use the `only_app` runtime-variable to only provision one WAF-App:

```bash
ansible-playbook ... -e only_app=app1 --tags rules
```

To debug errors - you can set the 'debug' variable at runtime:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e debug=yes
```
