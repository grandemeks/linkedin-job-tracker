# Sta Terraform vrati nakon apply (IP adresa servera...)
# Outputi su vrednosti koje Terraform ispise nakon apply
# Korisno za dobijanje IP adrese, DNS-a itd.

output "server_ip" {
  description = "Javna IP adresa servera"
  value       = aws_eip.main.public_ip
}

output "ssh_command" {
  description = "Komanda za SSH na server"
  value       = "ssh ubuntu@${aws_eip.main.public_ip}"
}

output "instance_id" {
  description = "AWS EC2 Instance ID"
  value       = aws_instance.main.id
}