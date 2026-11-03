# Week 2 · Networking and IAM

Ahmed Yassin Ahmed · Group 2 · Completed 3 November 2026

## Network inspection

The laptop runs Omarchy (Arch Linux). Its Wi-Fi interface `wlp0s20f3` has the local IPv4 address `10.2.68.139/20` and uses `10.2.64.1` as the default gateway. The address is private because it falls within the RFC 1918 range `10.0.0.0/8`. The /20 mask is `255.255.240.0`, so the laptop and gateway share the subnet `10.2.64.0/20`.

These laptop readings were supplied by Ahmed. The command transcripts in `evidence/` were captured in a separate Ubuntu lab environment.

## Divide 10.0.0.0/24 into four equal subnets
Borrowing two host bits gives four prefixes of length 26. Six host bits remain, so each block spans 64 addresses. A conventional IPv4 LAN has 62 usable hosts. An ordinary AWS VPC subnet reserves its first four addresses and its last one, leaving 59 assignable addresses.

| Network | Full range | Conventional host range | Broadcast | AWS assignable range | AWS count |
|---|---|---|---|---|---|
| 10.0.0.0/26 | .0–.63 | .1–.62 | .63 | .4–.62 | 59 |
| 10.0.0.64/26 | .64–.127 | .65–.126 | .127 | .68–.126 | 59 |
| 10.0.0.128/26 | .128–.191 | .129–.190 | .191 | .132–.190 | 59 |
| 10.0.0.192/26 | .192–.255 | .193–.254 | .255 | .196–.254 | 59 |

All shortened addresses begin with `10.0.0`. The adjacent network and broadcast boundaries account for the complete /24 without overlap.

## DNS and HTTPS
The system resolver returned exit code 2 for `example.com` and produced no IPv4 answer in the isolated lab. A terminal DNS-over-HTTPS query using curl against the Google Public DNS resolver returned status 0 and the addresses `104.20.23.154` and `172.66.147.243`. DNS translates a name into records that clients can use. A successful external lookup and a failed local lookup can coexist when the local resolver is unavailable.

The browser loaded the Example Domain page at `https://example.com`. A terminal HEAD request with `curl -I https://example.com` returned `HTTP/2 200`. The earlier HTTP/1.1 200 line was the proxy handshake. TLS authenticates the endpoint against a trusted certificate and protects data in transit against disclosure and modification. A DNS answer alone says nothing about route reachability, whether a service is listening, certificate validity, or whether the requested page exists.

[DNS lookup used in this exercise](https://dns.google/resolve?name=example.com&type=A) · [Command output](evidence/dns-https.txt)

## Read the response
| HTTP status | Interpretation | Example |
|---|---|---|
| 200 | The request succeeded | A GET returns the requested page. |
| 301 | The resource has a permanent new location | The old URL supplies a Location header. |
| 403 | The server refuses the request | A user lacks access to a protected object. |
| 404 | The requested resource was not found | A client asks for a missing path. |
| 500 | The server encountered an unexpected error | An unhandled exception interrupts a request. |

## IAM and least privilege
An IAM user has a persistent identity. A role supplies temporary credentials when assumed, for example by an application on EC2. Policies define which actions apply to which resources. In the [lab policy](s3-read-policy.json), Action grants only `s3:GetObject`, and Resource limits the grant to object keys in `example-bucket`. The trailing slash and wildcard select objects. Listing keys would require `s3:ListBucket` on the bucket ARN. This policy grants neither listing nor writes. If the identity is compromised, this grant cannot be used to overwrite objects, delete data, or modify bucket settings. A broader `s3:*` grant could allow those operations on applicable resources. Other applicable policies can still deny a request. Keeping access keys out of version control prevents a reader of the repository or its history from reusing them.

## Diagnose the failing layer
| Observation | First check |
|---|---|
| No address for the name | Compare the local resolver with an independent resolver and inspect DNS records. |
| Name resolves, connection times out | Check routing, the destination port, firewall and security-group rules. |
| Certificate warning | Inspect the hostname, validity dates and trust chain before sending data. |
| HTTP 404 | Verify the path and its application route. An HTTP server answered. |
| EC2 receives AccessDenied for an S3 object | Check the assumed role, bucket and object ARN, identity and bucket policies, explicit denies, and KMS permissions if applicable. |

Run `python3 check.py` on Linux to inspect the interface and routes and check the four subnet boundaries and IAM policy. The policy was validated locally. No AWS resources or permissions were changed.

[Network and policy checks](evidence/network-check.txt) · [AWS subnet sizing](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html) · [S3 GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html)
