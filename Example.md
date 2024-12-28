# Coraza WAF Example

Check out the [ansibleguy.infra_haproxy Example](https://github.com/ansibleguy/infra_haproxy/blob/latest/ExampleCorazaWAF.md) for a full integration example!

## Config

```yaml
waf:
  apps:
    - name: 'default'
    - name: 'default_block'
      block: true

    # apis
    - name: 'app1'
      block: true
      rules:
        vars:
          tx.allowed_methods: 'GET HEAD POST PUT OPTIONS'

        rule_changes:
          'REQUEST-933-APPLICATION-ATTACK-PHP.conf': false
          '`REQUEST-944-APPLICATION-ATTACK-JAVA.conf`':
            944100: false

          'REQUEST-941-APPLICATION-ATTACK-XSS.conf':
            941010: |
              SecRule REQUEST_FILENAME "!@validateByteRange 20, 45-47, 48-57, 65-90, 95, 97-122" \
                "id:941010,\
                phase:1,\
                pass,\
                t:none,\
                nolog,\
                tag:'OWASP_CRS',\
                ctl:ruleRemoveTargetByTag=xss-perf-disable;REQUEST_FILENAME,\
                ver:'OWASP_CRS/4.7.0'"
              # TEST
            

    - name: 'app2'
```

----

## Result

```bash
root@test-ag-haproxy-waf:/# cat /etc/haproxy/haproxy.cfg 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_haproxy
> 
> global
>     daemon
>     user haproxy
>     group haproxy
>
>     tune.ssl.capture-buffer-size 96
> 
>     log /dev/log    local0
>     log /dev/log    local1 notice
>     chroot /var/lib/haproxy
>     stats socket /run/haproxy/admin.sock mode 660 level admin
>     stats timeout 30s
>     ca-base /etc/ssl/certs
>     crt-base /etc/ssl/private
>     ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
>     ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
>     ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
>
> defaults
>     log global
>     mode http
>     option httplog
>     option dontlognull
>     timeout connect 5000
>     timeout client 50000
>     timeout server 50000
>     errorfile 400 /etc/haproxy/errors/400.http
>     errorfile 403 /etc/haproxy/errors/403.http
>     errorfile 408 /etc/haproxy/errors/408.http
>     errorfile 500 /etc/haproxy/errors/500.http
>     errorfile 502 /etc/haproxy/errors/502.http
>     errorfile 503 /etc/haproxy/errors/503.http
>     errorfile 504 /etc/haproxy/errors/504.http

root@test-ag-haproxy-waf:/# cat /etc/haproxy/waf-coraza.cfg 
> # Ansible managed
> # ansibleguy.haproxy_waf_coraza
> 
> backend coraza-waf-spoa
>     mode tcp
>     server coraza-waf 127.0.0.1:9000 check

root@test-ag-haproxy-waf:/# cat waf-coraza-spoe.cfg 
> # Ansible managed
> # ansibleguy.haproxy_waf_coraza
> 
> [coraza]
> spoe-agent coraza-agent
>     messages    coraza-req
>     groups      coraza-req
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
>
> spoe-group coraza-req
>     messages coraza-req

root@test-ag-haproxy-waf:/# cat /etc/haproxy/conf.d/frontend.cfg 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_haproxy
>  
> frontend fe_web
>     mode http
>     bind [::]:80 v4v6
>  
>     ...
>     http-request set-var(txn.waf_app) str(default_block) if be_test2_filter_domains
>     ...
>     http-request set-var(txn.waf_app) str(be_app1) if be_app1_filter_domains
>     ...
>     http-request set-var(txn.waf_app) str(be_app2) if be_app2_filter_domains
> 
>     # Coraza WAF
>     http-request set-var(txn.waf_app) str(default) if !{ var(txn.waf_app) -m found }
> 
>     filter spoe engine coraza config /etc/haproxy/waf-coraza-spoe.cfg
>     http-request send-spoe-group coraza coraza-req
>     http-request capture var(txn.waf_app) len 50
>     http-request capture var(txn.coraza.id) len 16
>     http-request capture var(txn.coraza.error) len 1
>     http-request capture var(txn.coraza.action) len 8
>     http-request deny status 403 default-errorfiles if { var(txn.coraza.action) -m str deny }
>     http-response deny status 403 default-errorfiles if { var(txn.coraza.action) -m str deny }
>     http-request silent-drop if { var(txn.coraza.action) -m str drop }
>     http-response silent-drop if { var(txn.coraza.action) -m str drop }

root@test-ag-haproxy-waf:/# systemctl status haproxy.service
> * haproxy.service - HAProxy Load Balancer
>      Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; preset: enabled)
>     Drop-In: /etc/systemd/system/haproxy.service.d
>              `-override.conf
>      Active: active (running) since Sat 2024-05-04 16:24:54 UTC; 4min 11s ago
>        Docs: man:haproxy(1)
>              file:/usr/share/doc/haproxy/configuration.txt.gz
>              https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/
>              https://github.com/ansibleguy/infra_haproxy
>     Process: 4574 ExecStartPre=/usr/sbin/haproxy -c -f $CONFIG -f /etc/haproxy/conf.d/ -f /etc/haproxy/waf-coraza.cfg (code=exited, status=0/SUCCESS)
>     Process: 4635 ExecReload=/usr/sbin/haproxy -c -f $CONFIG -f /etc/haproxy/conf.d/ -f /etc/haproxy/waf-coraza.cfg (code=exited, status=0/SUCCESS)
>     Process: 4637 ExecReload=/bin/kill -USR2 $MAINPID (code=exited, status=0/SUCCESS)
>    Main PID: 4576 (haproxy)
>      Status: "Ready."
>       Tasks: 7 (limit: 1783)
>      Memory: 132.2M
>         CPU: 297ms
>      CGroup: /system.slice/haproxy.service
>              |-4576 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/ -p /run/haproxy.pid -S /run/haproxy-master.sock
>              `-4639 /usr/sbin/haproxy -sf 4578 -x sockpair@4 -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/ -p /run/haproxy.pid -S /run/haproxy-master.sock

root@test-ag-haproxy-waf:/# systemctl status coraza-spoa.service 
> ● coraza-spoa.service - Coraza WAF SPOA Daemon
>      Loaded: loaded (/etc/systemd/system/coraza-spoa.service; enabled; preset: enabled)
>     Drop-In: /etc/systemd/system/coraza-spoa.service.d
>              └─override.conf
>      Active: active (running) since Fri 2024-12-27 19:45:29 CET; 1h 12min ago
>        Docs: https://www.coraza.io
>              https://github.com/corazawaf/coraza-spoa
>              https://github.com/corazawaf/coraza
>              https://coraza.io/docs/seclang/directives/
>              https://github.com/ansibleguy/haproxy_waf_coraza
>              https://docs.o-x-l.com/waf/coraza.html
>    Main PID: 3878168 (coraza-spoa)
>       Tasks: 10 (limit: 4531)
>      Memory: 11.7M
>         CPU: 4.099s
>      CGroup: /system.slice/coraza-spoa.service
>              └─3878168 /usr/bin/coraza-spoa -config=/etc/coraza-spoa/spoa.yml

root@test-ag-haproxy-waf:/# ls -l /etc/coraza-spoa/apps/be_log_ui/v4.7.0/@owasp_crs/*PHP*
> -rwxr-x--- 1 root coraza 17126 Dec 28 22:36 /etc/coraza-spoa/apps/app1/v4.7.0/@owasp_crs/REQUEST-933-APPLICATION-ATTACK-PHP.conf.disabled
> -rwxr-x--- 1 root coraza  4487 Dec 27 15:55 /etc/coraza-spoa/apps/app1/v4.7.0/@owasp_crs/RESPONSE-953-DATA-LEAKAGES-PHP.conf

root@test-ag-haproxy-waf:/# cat /etc/coraza-spoa/apps/app1/v4.7.0/@owasp_crs/REQUEST-944-APPLICATION-ATTACK-JAVA.conf
> ...
> SecRule TX:DETECTION_PARANOIA_LEVEL "@lt 1" "id:944012,phase:2,pass,nolog,tag:'OWASP_CRS',ver:'OWASP_CRS/4.7.0',skipAfter:END-REQUEST-944-APPLICATION-ATTACK-JAVA"
> #SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|REQUEST_BODY|REQUEST_HEADERS|XML:/*|XML://@* \
> #    "@rx java\.lang\.(?:runtime|processbuilder)" \
> #    "id:944100,\
> #    phase:2,\
> #    block,\
> #    t:none,t:lowercase,\
> #    msg:'Remote Command Execution: Suspicious Java class detected',\
> #    logdata:'Matched Data: %{MATCHED_VAR} found within %{MATCHED_VAR_NAME}',\
> #    tag:'application-multi',\
> #    tag:'language-java',\
> #    tag:'platform-multi',\
> #    tag:'attack-rce',\
> #    tag:'paranoia-level/1',\
> #    tag:'OWASP_CRS',\
> #    tag:'capec/1000/152/137/6',\
> #    tag:'PCI/6.5.2',\
> #    ver:'OWASP_CRS/4.7.0',\
> #    severity:'CRITICAL',\
> #    setvar:'tx.rce_score=+%{tx.critical_anomaly_score}',\
> #    setvar:'tx.inbound_anomaly_score_pl1=+%{tx.critical_anomaly_score}'"
> SecRule ...
> ...

root@test-ag-haproxy-waf:/# cat /etc/coraza-spoa/apps/app1/v4.7.0/@owasp_crs/REQUEST-941-APPLICATION-ATTACK-XSS.conf
> ...
> SecRule REQUEST_FILENAME "!@validateByteRange 20, 45-47, 48-57, 65-90, 95, 97-122" \
>     "id:941010,\
>     phase:1,\
>     pass,\
>     t:none,\
>     nolog,\
>     tag:'OWASP_CRS',\
>     ctl:ruleRemoveTargetByTag=xss-perf-disable;REQUEST_FILENAME,\
>     ver:'OWASP_CRS/4.7.0'"
> # TEST
> ...
```