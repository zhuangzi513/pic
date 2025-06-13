# **后端功能和实现方式**

后端主要完成以下几个功能：

+ 1 PIC相关：
+ 1.1 解析video文件，将目标帧数据保存为pic，[yolo]；
+ 1.2 对比两个pic是否是同一个实体[triple ResNet]；
+ 2 DB相关：
+ 2.1 保存video文件中提取到的pic信息，及其他信息（pic，size，platform，date，category，price）保存到DB中；
+ 2.2 根据输入信息（size，category，pic），与DB中保存的数据比对后，给出TOP8匹配结果；
具体描述和实现方式如下所述

## **PIC处理相关技术路径**

为了获取更多的数据，需要实现抓取线上数据的程序，这部分会因为线上资源的策略的调整，频繁改动对应的程序实现。

为了实现对video文件的解析，在video playing的同时，使用yolo模型对每一帧数据进行判断，并将目标区域以指定格式，指定文件名格式，保存到指定的文件目录。这期间涉及到的技术实现方案包括yolo的模式识别，opencv使用，格式定义等细节实现。


### **线上资源获取的技术方案介绍**
略。

### **yolo相关的技术方案介绍**

在使用yolo完成上述功能之前，首先需要对yolo的不同版本的特点有基本了解。基本每一个版本的YOLO都会细分为以下几种细分版本，分别适用于不同的应用场景下，以YOLOv8这个版本为例，它对应的细分版本如下表所示：

|模型版本|参数量|mAP@0.5:0.95 (COCO)|推理速度 (FPS)*| 适用场景|
|-------|------|-------------------|--------------|--------|
|YOLOv8n|~3.2M|37.3|300+ (T4 GPU)| 超轻量级移动端/边缘设备|
|YOLOv8s|~11.4M|44.9|~150|平衡型（通用嵌入式设备）|
|YOLOv8m|~25.9M|50.2|~90|中等精度需求（工业级应用）|
|YOLOv8l|~43.7M|52.9|~60|高精度检测（服务器/云端）|
|YOLOv8x|~68.2M|53.9|~40|极致精度（复杂场景/研究）|

#### **YOLO版本选择和fine-tuning**

我们选择v8x，如果后续有性能和精度更优的版本，我们也会适时调整模型的版本，甚至选择其他的模型。
在对预训练的YOLOv8进行fine-tuning之前，首先需要明确以下几件事：

- 训练时使用PIC尺寸：416x416，640x640，1280x1280;
- PIC的格式：支持常见的几种PIC格式（JPG/JPEG/PNG/BMP）；
- 因为预训练的参数中已经积累了很多图片学习知识，所以fine-tuning需要冻结一些层的参数，通常只保留用于分类的最后一个FC层；
- 期望的fine-tuning后的目标分类（category）需要重新定义。

##### **category定义**

category的定义只是一个整数类型数据，需要建立该整数和具体分类名称之间的映射关系，而且为了和下游的DB数据处理统一格式，YOLO这里建立的整数和具体分类名称的分类至关重要，这里的对应关系会一直延续到最下游的应用环节。为了后向兼容可能新增的分类名称，整数的定义需要有重足的stride。比如下所表所示：

|category ID值|category名称|可能需要的具体描述|
|-------------|------------|------------------|
|1            |WSP         |暂无              |
|2            |RED-WSP     |暂无              |
|3            |GRE-WSP     |暂无              |
|4            |BLU-WSP     |暂无              |
|12           |NUO-RED-WSP |暂无              |
|13           |NUO-GRE-WSP |暂无              |
|14           |NUO-BLU-WSP |暂无              |
|22           |ICE-RED-WSP |暂无              |
|23           |ICE-GRE-WSP |暂无              |
|24           |ICE-BLU-WSP |暂无              |
|100          |FG          |暂无              |
|200          |JZ          |暂无              |
|300          |ED          |暂无              |
|400          |ED          |暂无              |

上述对category的定义虽然方便了后续DB处理，但是因为YOLO在训练时只支持连续的分类（0,1,2,3,4 ...）值，所以在**数据标注**，**模型训练**，**推理**这三个阶段都需要特殊处理。

- **数据标注阶段**
在标注文件（如 YOLO 格式的 .txt 文件）中，直接使用非连续值：

```text
# 标注文件示例（class_id x_center y_center width height）
100 0.5 0.5 0.2 0.3  # class=100
200 0.3 0.7 0.1 0.1  # class=200
```

- **模型训练阶段**
fine-tuning时需要修改数据集配置文件**data.yaml**，明确指定类别名称(0,1,2,3 ...)和对应的自定义值(100,200,300,400 ...)之间的对应关系，如下所示：

```text
names:
  0: 100  # 模型输出0对应实际类别100
  1: 200  # 模型输出1对应实际类别200
```

- **模型推理阶段**
模型输出的 class 是连续的（如 0, 1），需通过映射表转换回原始值：

```python
class_mapping = {0: 100, 1: 200}  # 与data.yaml一致
predicted_class = class_mapping[raw_output_class]
```

##### **标记和存储**

以下是 **10 款常用标注软件**的对比表格，包含平台、标注类型、协作功能、支持格式和适用场景等核心信息：

---

**标注软件对比总表**

| 工具名称         | 平台/类型       | 标注类型                | 支持格式                           | 协作功能 | 适用场景                     | 官网/下载链接                                  |
|------------------|----------------|-------------------------|------------------------------------|----------|------------------------------|-----------------------------------------------|
| **LabelImg**     | 桌面（开源）    | 矩形框                  | YOLO, Pascal VOC, COCO             | ❌        | 小规模目标检测               | [GitHub](https://github.com/HumanSignal/labelImg) |
| **Labelme**      | 桌面（开源）    | 多边形/矩形/点          | JSON (COCO兼容)                    | ❌        | 精细分割（医学/遥感）        | [GitHub](https://github.com/wkentaro/labelme)    |
| **CVAT**         | Web/本地（开源）| 矩形/多边形/视频/点     | YOLO, COCO, VOC, TFRecord          | ✅        | 企业级大规模标注             | [官网](https://cvat.org/)                       |
| **Roboflow**     | 在线（免费+付费）| 矩形/多边形/AI预标注    | YOLO, COCO, TFRecord, CSV          | ✅        | 快速迭代的团队项目           | [官网](https://roboflow.com/)                   |
| **VIA (VGG)**    | 在线（开源）    | 多边形/矩形/点          | JSON, COCO                         | ❌        | 学术研究或简单标注           | [官网](https://www.robots.ox.ac.uk/~vgg/software/via/) |
| **Supervisely**  | 在线（免费+付费）| 2D/3D/视频/点          | COCO, YOLO, VOC                    | ✅        | 专业团队多模态标注           | [官网](https://supervisely.com/)                |
| **MakeSense.ai** | 在线（免费）    | 矩形框/分类标签         | YOLO, COCO, CSV                    | ❌        | 临时或小型项目               | [官网](https://www.makesense.ai/)               |
| **RectLabel**    | macOS（付费）   | 矩形/多边形             | YOLO, COCO, VOC                    | ❌        | Mac用户的本地标注            | [官网](https://rectlabel.com/)                  |
| **Label Studio** | Web/本地（开源）| 多模态（文本/图像/音频）| JSON, COCO, YOLO                   | ✅        | 复杂任务（如多模态数据）     | [官网](https://labelstud.io/)                   |
| **Diffgram**     | Web/本地（开源）| 矩形/视频/3D           | YOLO, COCO, VOC                    | ✅        | 企业级数据管道               | [官网](https://diffgram.com/)                   |

---

**关键对比维度**

- **平台兼容性**：  
  - 桌面端：LabelImg、Labelme、RectLabel（Mac专属）。  
  - 在线工具：Roboflow、MakeSense.ai、Supervisely。  
  - 可自托管：CVAT、Label Studio、Diffgram。  

- **标注类型**：  
  - **矩形框**：LabelImg、MakeSense.ai（适合目标检测）。  
  - **多边形/点**：Labelme、VIA（适合分割任务）。  
  - **视频/3D**：CVAT、Supervisely（适合时序数据）。  

- **协作与扩展**：  
  - **团队协作**：CVAT、Supervisely、Diffgram（支持用户权限管理）。  
  - **AI辅助**：Roboflow、Supervisely（预标注模型加速标注）。  

- **导出格式**：  
  - **YOLO格式**：所有工具均支持（需注意坐标归一化）。  
  - **COCO格式**：Labelme、CVAT、Roboflow（适合学术界）。  

---

**推荐选择指南**

- **个人开发者**：LabelImg（简单）或 Labelme（分割）。  
- **团队项目**：CVAT（自托管）或 Roboflow（云端）。  
- **Mac用户**：RectLabel（本地高效标注）。  
- **多模态数据**：Label Studio（文本+图像+音频）。  

---

**标注软件生成的标注文件的目录结构，以及文件命名格式，以及文件内容**
标注软件生成的标注文件的目录结构通常如下所示：

```text
#目录结构
dataset/
├── images/                  # 原始图像文件夹
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── annotations/             # 标注文件文件夹
│   ├── image1.xml           # LabelImg格式（PASCAL VOC）
│   ├── image1.json          # LabelMe/COCO格式
│   └── ...
└── labels/                  # YOLO格式专用文件夹（可选）
    ├── image1.txt
    └── ...
```

其中labels目录下包的 **.txt**文件是YOLO专属的标注格式的文件，其内容如下：

```text
#class_id center_x center_y width height（归一化坐标，0~1）
0 0.5 0.6 0.2 0.3
1 0.1 0.1 0.05 0.05
```

---

**YOLO fine-tuning需要的标注文件的目录结构，以及文件命名格式**


参考frame_ops/yolo_fine_tuning/readme
《此处略》

---

#### **使用Yolo解析video文件**

通过上述对YOLO的fine-tuning，就可以使用Fine-tuning以后的YOLO对VIDEO处理，以从VIDEO中截取包含我们定义的那些category类别的物品的帧数据，继而把提取到的帧数据保存到DB中。其中需要留意的几个关键点是：
- 保存的帧数据会继续用于对YOLO的**继续fine-tuning**，所以保存的帧数据需要尽量符合Fine-tuning的输入PIC的size，即：416x416/640x640/1280x1280;
- 帧数据在保存成文件时，需要按照**固定命名格式**命名，并存到指定目录下(date/vendor/file.png)；
- 因为前期可能会出现对帧数据的分类不准确的情况，此时需要人工纠正。为了方便纠正，需要在YOLO处理帧数据时，将**帧数据的完整信息**保存到CSV/EXCEL文件中。
对上述**继续fine-tuning**，**固定命名格式**和**帧数据的完整信息**的具体定义如下：


**继续fine-tuning**
有两个方面的考虑：
- 开始时YOLO的识别精度可能会较低，所以需要持续提高YOLO的识别精度。为了能够持续提高YOLO的识别精度，需要不断对YOLO做fine-tuning以使其精度和准确度越来越高；
- 随着时间的推移，可能需要实现从VIDEO中提取更多种类物品的帧数据，为了使YOLO能够识别更多种类（category），后续也需要对YOLO持续fine-tuning。


**固定命名格式**
综合windows和linux对文件名长度的限制（<255 charaters）,对文件的命名格式定义如下：
|CATEGORY_ID(PIN LEI)|QUALITY(ZHONG SHUI)|COLOR |LENGTH|WIDTH|HEIGHT|PRICE|
|--------------------|-------------------|------|------|-----|------|-----|
|0000-9999           |00-99              |00-99 |00-99 |00-99|00-99 |0-9999999|
|4Byte               |2Byte              |2Byte |2Byte |2Byte|2Byte |7Byte|

下面是一个文件的命名示例

```text
#CATEGORY_ID : 0020
#QUALITY     : 12
#COLOR       : 23
#LENGTH      : 11
#WIDTH       : 03
#HEIGHT      : 02
#PRICE       : 34567
0020_12_23_11_03_02_0034567.png
```

其中CATEGORY，COLOR和QUALITY均有一个MAP，将数值映射到Human Recognizeable的名称。

**帧数据的完整信息** {#anchor1}
因为帧数据的完整信息不仅是用于人工纠正的，而且最终将帧数据保存到DB的操作也是依赖于CSV格式的完整帧数据信息。所以对所谓帧数据的**完整信息**定义如下：
|**VENDOR_ID**|DATE|TIME|CATEGORY|QUALITY|COLOR|WIDTH|HEIGHT|PRICE|VIDEO_PATH|**O_PIC_PATH**|**C_PIC_PATH**|
|-------------|----|----|--------|-------|-----|-----|------|-----|----------|--------------|--------------|
|-**平台名称**-|----|----|--------|-------|-----|-----|------|-----|----------|-**解析生成**--|-**解析生成**-|

对各个字段的解释如下：

```text
# VENDOR_ID : Platform name，如YueGuangQingCheng；
# DATE      ：Video的发生日期
# TIME      ：帧在Video中的相对时间
# CATEGORY  ：物品类别，整数值，可以通过定义的Map映射到Human Recognizeable的名称
# QUALITY   ：质量信息，整数值，可以通过定义的MAP映射到Human Recognizeable的名称
# COLOR     ：颜色信息，整数值，可以通过定义的MAP映射到Human Recognizeable的名称
# WIDTH     : SIZE信息的一种，对应的信息不一定为宽度，可能是圈口的内圈
# LENGTH    ：SIZE信息的一种，对应的信息不一定为长度，可能是圈口的外圈
# HEIGHT    ：厚度
# PRICE     ：字面含义，整数
# VIDEO_PATH：字面含义
#>>>>>>>>>>>>>>>>>>>>>>以上部分是原始信息<<<<<<<<<<<<<<<<<<<<<<<
#>>>>>>>>>>>>>>>>>>>>>>以下部分是生成信息<<<<<<<<<<<<<<<<<<<<<<<
# O_PIC_PATH：original PIC文件名，没有经过YOLO裁剪，根据矫正以后的原始信息重新生成的字段，直接用于后续DB操作
# C_PIC_PATH: crapped PIC文件名，YOLO裁剪过后的文件名，根据矫正以后的原始信息重新生成的字段，直接用于后续DB操作

```
**----------------------------------------------------------分割线----------------------------------------------------------**

### **PIC比对**
根据User的输入信息(USER_INPUT)，从当前保存的数据中找出与USER_INPUT数据最接近的TOP8数据。其中最重要的一项功能是PIC之间的相似度比较。为了实现这个功能，需要借助AI模型（暂定ResNet+Trplet Loss）。其中又会涉及到模型的fine tuning。

#### **模型选择（resnet+Triplet Loss）**

#### **模型的fine tuning**

#### **比对结果的存储和格式定义**


## **DB（数据库）相关功能描述**

DB主要分为三大类：

- 一类数据：根据YOLO和其他方式获取到的PIC数据（称为内部数据，对外隐藏）构建的PIC数据库，用于和User输入的数据做比对和相似度查询；
- 二类数据：User主动提供的原始数据（如：PIC，price，size），UserInfo（如：ID，level，）；
- 三类数据：在二类数据的基础之上，在程序运行期间生成的数据（如：Comments，TopList）；

上述三类数据，根据数据库设计原则，每一种数据都需包含了多种表和视图。而且，为了保证程序的响应效率，每一种表都需要精心设计其列信息，同时保证后向兼容（未来可能的修改）。


### 一类数据DB构建

DB对内接收YOLO的计算结果，以及其他方式获取到的类似YOLO计算结果的信息；对外提供普通数据库查询；为了提高查询的效率，和程序相应效率，需要对DB中的数据组织方式定义清楚。其中涉及的组织方式有以下几个方面：

- 数据存储方式：主键（各个表中通用primary key）的定义，表的定义和分类；
- DB的更新机制：什么情况下触发数据库的更新，更新哪些表，如何避免尽量少的更新；
- 视图的定义：设计视图的定义，保证DB不断更新数据的情况下，对外提供的API不用改变（API改变的话，会导致前端的代码也会随之改动，引发稳定性危机）；

#### 表的分类和定义

表主要分为两类：
- 从VIDEO中提取PIC，对应的表；
- 其他方式获取到PIC，对应的表；

表的定义：
上述两种表因为都是同一类原始数据，应该有同样的格式。参考上述**帧数据的完整信息** (#anchor1)

#### 视图的分类和定义

### 二类数据DB构建

#### 表的分类和定义

#### 视图的分类和定义

### 三类数据DB构建

#### 表的分类和定义

#### 视图的分类和定义
