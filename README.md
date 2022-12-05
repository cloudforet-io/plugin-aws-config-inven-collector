# plugin-aws-config-inven-collector
Plugin for AWS Config Results

---

## Secret Data
*Schema*
* aws_access_key_id (str): AWS Access Key
* aws_secret_access_key (str): AWS Secret Access Key
* role_arn (str): ARN for Assume Role (Optional)
* external_id (str): External ID for Assume Role (Optional)

*Example*
<pre>
<code>
{
    "aws_access_key_id": "*****",
    "aws_secret_access_key": "*****",
    "role_arn": "arn:aws:iam::*****",
    "external_id": "*****"
}
</code>
</pre>

## Options
*Schema*
* conformance_pack_names (list): Set a Specific Conformance Pack Names


*Example*
<pre>
<code>
{
    "conformance_pack_names": [
        "spaceone-irm-security-audit-pack",
        ...
    ]
}
</code>
</pre>