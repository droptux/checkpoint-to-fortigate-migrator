Arquitetura da ferramenta de migração

Vamos dividir em 3 scripts principais.

checkpoint_migration/
│
├── config.py
├── logger.py
├── checkpoint_client.py
│
├── extract_checkpoint.py
├── parse_checkpoint.py
├── generate_fortigate.py
│
└── output/

Primeiro vamos construir a parte crítica: extração confiável da API.

Fluxo do script de extração

O script irá executar:

1 login API
2 listar policy packages
3 extrair objetos
4 extrair serviços
5 extrair grupos
6 extrair policies
7 extrair NAT
8 salvar JSON organizado
Estrutura de saída
output/

objects/
    hosts.json
    networks.json
    ranges.json
    groups.json

services/
    tcp.json
    udp.json
    icmp.json
    service_groups.json

policies/
    firewall_externo.json
    firewall_vpn.json
    firewall_interno.json

nat/
    nat_externo.json
    nat_vpn.json
    nat_interno.json

logs/
    extractor.log