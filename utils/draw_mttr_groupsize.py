import matplotlib.pyplot as plt

import pandas as pd

mttr_list = [[],[]]
QoI_list = [[],[]]
for i, filename in enumerate(["True", "False"]):

    for folder in ["K0", "K3", "K5", "K10", "K15", "K20"]:
        input_path = f"/Users/shuqinzhu/Desktop/dragon/{folder}/dragon_D1_R10_T60_S6_P{filename}/dragon_D1_R10_T60_S6_P{filename}_final_report.xlsx"

        metrics_df = pd.read_excel(input_path, sheet_name='Metrics')

        print(folder)

        # Get the value from the "metrics" sheet
        mttr_list[i].append(metrics_df[metrics_df.iloc[:, 1] == "Avg MTTR"].iloc[0, 2])
        QoI_list[i].append(metrics_df[metrics_df.iloc[:, 1] == "QoI After Reset"].iloc[0, 2])


plt.figure()
pri_line, = plt.plot([0, 3, 5, 10, 15, 20], mttr_list[0], marker='o', label=f'With Priority Queue')

nopri_line, = plt.plot([0, 3, 5, 10, 15, 20], mttr_list[1], marker='x', label=f'No Priority Queue')

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)


# Set x-axis to only show values in group_sizes list
plt.xticks([0, 3, 5, 10, 15, 20])

ax.set_ylabel('Mean Time To Repair (MTTR)', loc='top', rotation=0, labelpad=-140)
ax.set_xlabel('Group Size (G)', loc='right')
plt.tight_layout()


plt.text(6, 44, 'With Priority Queue', color=pri_line.get_color(), fontweight='bold')

plt.text(6, 53, 'No Priority Queue', color=nopri_line.get_color(), fontweight='bold')

# Add legend
# plt.show(dpi=500)
plt.savefig(f"../dragon_MTTR_groupsize_compare.png", dpi=500)
plt.close()

plt.figure()
pri_line, = plt.plot([0, 3, 5, 10, 15, 20], QoI_list[0], marker='o', label=f'With Priority Queue')

nopri_line, = plt.plot([0, 3, 5, 10, 15, 20], QoI_list[1], marker='x', label=f'No Priority Queue')


plt.text(8, 0.45, 'With Priority Queue', color=pri_line.get_color(), fontweight='bold')

plt.text(8, 0.32, 'No Priority Queue', color=nopri_line.get_color(), fontweight='bold')
# plt.tight_layout()

ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Set x-axis to only show values in group_sizes list
plt.xticks([0, 3, 5, 10, 15, 20])

ax.set_ylabel('Quality of Illumination (QoI)', loc='top', rotation=0, labelpad=-133)
ax.set_xlabel('Group Size (G)', loc='right')
plt.tight_layout()
# Add legend
# plt.show(dpi=500)
plt.savefig(f"../dragon_QoI_groupsize_compare.png", dpi=500)
plt.close()