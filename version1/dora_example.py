import pandas as pd
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

# Simulated dataset representing deployment events
# Each row includes deployment timestamp, success/failure status, and time to restore (if failed)
data = {
    'commit_id': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'],
    'commit_time': [
        datetime.datetime(2025, 8, 1, 10, 0),
        datetime.datetime(2025, 8, 2, 14, 0),
        datetime.datetime(2025, 8, 3, 9, 0),
        datetime.datetime(2025, 8, 3, 15, 0),
        datetime.datetime(2025, 8, 5, 11, 0),
        datetime.datetime(2025, 8, 7, 16, 0),
        datetime.datetime(2025, 8, 10, 12, 0),
        datetime.datetime(2025, 8, 12, 17, 0)
    ],
    'deploy_time': [
        datetime.datetime(2025, 8, 1, 12, 0),
        datetime.datetime(2025, 8, 2, 16, 30),
        datetime.datetime(2025, 8, 3, 10, 15),
        datetime.datetime(2025, 8, 3, 16, 0),
        datetime.datetime(2025, 8, 5, 12, 30),
        datetime.datetime(2025, 8, 7, 18, 0),
        datetime.datetime(2025, 8, 10, 14, 0),
        datetime.datetime(2025, 8, 12, 19, 30)
    ],
    'success': [True, True, False, True, True, False, True, True],
    'restore_time': [
        None, None, 
        datetime.datetime(2025, 8, 3, 11, 0), 
        None, None, 
        datetime.datetime(2025, 8, 7, 19, 30), 
        None, None
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate DORA Metrics
def calculate_dora_metrics(df, start_date, end_date):
    # Filter data for the given time period
    df_period = df[(df['deploy_time'] >= start_date) & (df['deploy_time'] <= end_date)]
    
    # 1. Deployment Frequency (deployments per day)
    total_days = (end_date - start_date).days
    deployment_count = len(df_period)
    deployment_frequency = deployment_count / total_days if total_days > 0 else 0
    
    # 2. Lead Time for Changes (average time from commit to deploy)
    df_period['lead_time'] = (df_period['deploy_time'] - df_period['commit_time']).dt.total_seconds() / 3600  # in hours
    lead_time_avg = df_period['lead_time'].mean()
    
    # 3. Change Failure Rate (percentage of failed deployments)
    failure_count = len(df_period[df_period['success'] == False])
    change_failure_rate = (failure_count / deployment_count * 100) if deployment_count > 0 else 0
    
    # 4. Mean Time to Restore (average time to recover from failures)
    df_failures = df_period[df_period['success'] == False].copy()
    df_failures['restore_duration'] = (df_failures['restore_time'] - df_failures['deploy_time']).dt.total_seconds() / 3600  # in hours
    mean_time_to_restore = df_failures['restore_duration'].mean() if not df_failures.empty else 0
    
    return {
        'Deployment Frequency (per day)': deployment_frequency,
        'Lead Time for Changes (hours)': lead_time_avg,
        'Change Failure Rate (%)': change_failure_rate,
        'Mean Time to Restore (hours)': mean_time_to_restore
    }

# Define analysis period (e.g., one month)
start_date = datetime.datetime(2025, 8, 1)
end_date = datetime.datetime(2025, 8, 31)

# Calculate metrics
metrics = calculate_dora_metrics(df, start_date, end_date)

# Print results
print("DORA Metrics for the period:", start_date.strftime('%Y-%m-%d'), "to", end_date.strftime('%Y-%m-%d'))
for key, value in metrics.items():
    print(f"{key}: {value:.2f}")

# Visualize Deployment Frequency over time
df['deploy_date'] = df['deploy_time'].dt.date
deployments_per_day = df.groupby('deploy_date').size()
plt.figure(figsize=(10, 5))
deployments_per_day.plot(kind='bar', color='skyblue')
plt.title('Deployments Per Day')
plt.xlabel('Date')
plt.ylabel('Number of Deployments')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
