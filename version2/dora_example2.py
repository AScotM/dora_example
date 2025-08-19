import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Simulated dataset
data = {
    'commit_id': ['c1','c2','c3','c4','c5','c6','c7','c8'],
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

df = pd.DataFrame(data)

def calculate_dora_metrics(df, start_date, end_date):
    # Subset with .copy() to avoid warnings
    df_period = df[(df['deploy_time'] >= start_date) & (df['deploy_time'] <= end_date)].copy()
    
    # Deployment Frequency (per day)
    total_days = (end_date - start_date).days + 1
    deployment_count = len(df_period)
    deployment_frequency = deployment_count / total_days if total_days > 0 else 0
    
    # Lead Time
    df_period['lead_time'] = (df_period['deploy_time'] - df_period['commit_time']).dt.total_seconds() / 3600
    lead_time_avg = df_period['lead_time'].mean()
    
    # Change Failure Rate
    failure_count = len(df_period[df_period['success'] == False])
    change_failure_rate = (failure_count / deployment_count * 100) if deployment_count > 0 else 0
    
    # Mean Time to Restore (only include failures with restore_time)
    df_failures = df_period[df_period['success'] == False].copy()
    df_failures = df_failures.dropna(subset=['restore_time'])
    df_failures['restore_duration'] = (df_failures['restore_time'] - df_failures['deploy_time']).dt.total_seconds() / 3600
    mean_time_to_restore = df_failures['restore_duration'].mean() if not df_failures.empty else 0
    
    return {
        'Deployment Frequency (per day)': deployment_frequency,
        'Lead Time for Changes (hours)': lead_time_avg,
        'Change Failure Rate (%)': change_failure_rate,
        'Mean Time to Restore (hours)': mean_time_to_restore
    }

# Analysis period
start_date = datetime.datetime(2025, 8, 1)
end_date = datetime.datetime(2025, 8, 31)

# Calculate metrics
metrics = calculate_dora_metrics(df, start_date, end_date)

print("DORA Metrics for period:", start_date.date(), "to", end_date.date())
for k,v in metrics.items():
    print(f"{k}: {v:.2f}")

# Visualization
df['deploy_date'] = df['deploy_time'].dt.date
deployments_per_day = df.groupby('deploy_date').size()

plt.figure(figsize=(10,5))
deployments_per_day.plot(kind='bar', color='skyblue')
plt.title('Deployments Per Day')
plt.xlabel('Date')
plt.ylabel('Number of Deployments')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
