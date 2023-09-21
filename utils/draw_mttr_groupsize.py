import matplotlib.pyplot as plt


plt.figure()
plt.plot([3, 5, 10, 20], [108.17, 118.11, 232.67, 1339.43], marker='o', label=f'With Priority Queue')

plt.plot([3, 5, 10, 20], [5.15, 3.85, 3.15, 1.38], marker='o', label=f'No Priority Queue')

# plt.tight_layout()

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Configure the chart
plt.xlabel('Group Size (G)')
plt.ylabel('Mean Time To Repair (MTTR)')

# Set x-axis to only show values in group_sizes list
plt.xticks([0, 3, 20])

# Add legend
plt.legend()
plt.savefig(f"../butterfly_MTTR_groupsize.png", dpi=500)
plt.close()