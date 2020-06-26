.PHONY: edit-vault
edit-vault:
	ansible-vault edit vars/private.yml

.PHONY: deploy
deploy:
	ansible-playbook --ask-vault-pass playbook.yml -i hosts.ini -l staging
