# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "sample-alarm-cpuutilization-web01-warn"
resource "aws_cloudwatch_metric_alarm" "sample_alarm" {
  actions_enabled     = true
  alarm_actions       = []
  alarm_description   = "web1server cpuutilization notification"
  alarm_name          = "sample-alarm-cpuutilization-web01-warn"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    InstanceId = "i-08fb7c7ac692ded9c"
  }
  evaluate_low_sample_count_percentiles = null
  evaluation_periods                    = 1
  extended_statistic                    = null
  insufficient_data_actions             = []
  metric_name                           = "CPUUtilization"
  namespace                             = "AWS/EC2"
  ok_actions                            = ["arn:aws:sns:ap-northeast-1:775115982694:Default_CloudWatch_Alarms_Topic_OK"]
  period                                = 300
  statistic                             = "Average"
  tags                                  = {}
  tags_all                              = {}
  threshold                             = 70
  threshold_metric_id                   = null
  treat_missing_data                    = "missing"
  unit                                  = null
}

# __generated__ by Terraform from "sample"
resource "aws_cloudwatch_dashboard" "sample_dashboard" {
  dashboard_body = "{\"widgets\":[]}"
  dashboard_name = "sample"
}
