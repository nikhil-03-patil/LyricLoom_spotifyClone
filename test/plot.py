import matplotlib.pyplot as plt

# Generate some sample data
activity_dates = ['2022-01-01', '2022-01-02', '2022-01-03']
activity_counts = [10, 15, 20]

# Plot the graph
plt.bar(activity_dates, activity_counts)
plt.xlabel('Date')
plt.ylabel('Activity Count')
plt.title('User Activity Over Time')
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust layout to prevent clipping of labels
plt.savefig('static/user_activity_graph.png')  # Save the graph as an image file
