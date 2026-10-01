#!/usr/bin/env bash
# Remove everything launch.sh made, so nothing keeps costing anything.
# An Elastic IP that is not attached to a running instance is billed, so this
# releases it too.
set -euo pipefail

REGION="${REGION:-us-east-1}"
NAME="${NAME:-teamsync}"

instances=$(aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)

if [ -n "$instances" ]; then
  echo "terminating: $instances"
  aws ec2 terminate-instances --region "$REGION" --instance-ids $instances >/dev/null
  aws ec2 wait instance-terminated --region "$REGION" --instance-ids $instances
fi

allocation=$(aws ec2 describe-addresses --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAME" --query 'Addresses[0].AllocationId' --output text)
if [ "$allocation" != "None" ] && [ -n "$allocation" ]; then
  echo "releasing address $allocation"
  aws ec2 release-address --region "$REGION" --allocation-id "$allocation"
fi

# The security group cannot go until the instance is really gone, hence the wait above.
group=$(aws ec2 describe-security-groups --region "$REGION" \
  --filters "Name=group-name,Values=$NAME" --query 'SecurityGroups[0].GroupId' --output text)
if [ "$group" != "None" ] && [ -n "$group" ]; then
  echo "deleting security group $group"
  aws ec2 delete-security-group --region "$REGION" --group-id "$group" || \
    echo "(still in use — try again in a minute)"
fi

echo "key pair $NAME kept; delete it with: aws ec2 delete-key-pair --region $REGION --key-name $NAME"
echo "done"
