# Open5GS Configuration File Changes

In February 2023, Open5GS changed the configuration file format which meant that Open5GS no longer started. To make this process easier the next time the config file format changes, I decided to document what parts of the file we had changed.

1. In the `parameter:` block, add the `use_openair: true` option.
2. In the `mme:` block:
    1. Change the `s1ap` property `addr:` to `192.168.1.1`
    2. Change the `gummei: plmn_id: mcc:` property to `208`
    3. Change the `gummei: plmn_id: mnc:` property to `93`
    4. Change the `tai: plmn_id: mcc:` property to `208`
    5. Change the `tai: plmn_id: mnc:` property to `93`
3. In the `spgw:` block, change the `gtpc: addr:` property to `192.168.1.1`
4. In the `smf:` block, comment out the `sbi:` block.
5. In the `sgwu:` block, change the `gtpu: addr:` property to `192.168.1.1`
6. Comment out the entire `nrf:` block.
