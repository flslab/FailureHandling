import matplotlib.pyplot as plt


plt.figure()
plt.plot([0, 3, 5, 10, 20], [1.39599053 + 0.7124796170504613,
                             0.607749449 + 0.14734894246205515,
                             0.5722433476 + 0.15772078400583267,
                             2.259141665 + 1.569578161139223,
                             0.5421206005 + 0.18231004135653098], marker='o', label=f'With Priority Queue')

plt.plot([0, 3, 20], [0.2051978463+0.11640856933626184, 3.044929713+5.380475370830152, 0.08307360836+1.2068793672327065], marker='o', label=f'No Priority Queue')

# plt.tight_layout()

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Configure the chart
plt.xlabel('Group Size (G)')
plt.ylabel('Mean Time To Repair (MTTR)')

# Set x-axis to only show values in group_sizes list
plt.xticks([0, 3, 5, 10, 15, 20])

# Add legend
plt.legend()
plt.savefig(f"../butterfly_MTTR_groupsize_compare.png", dpi=500)
plt.close()