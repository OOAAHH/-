《纯阳别册》
------------------------------------------

- "纯阳"在道教中通常指的是一种纯净无杂的阳性原则，也是道教历史上著名的人物吕洞宾的尊号，他被认为是达到了道教修炼的最高境界——纯阳无极。"别册"则通常指的是附录、补遗或是特别编制的册子，有时候也指独立出版的特殊书籍或文集。

- 将`《纯阳别册》`翻译成英文时，可以根据上下文的不同有不同的方式。如果是作为道教文化或修炼方法的讨论，可以翻译为 `"The Annex of Pure Yang"`或 `"The Supplement of Pure Yang"`，强调其作为补充材料或特别辑的性质。如果是强调书中内容或特定的修炼方法，也可以翻译为 `"The Pure Yang Manual"` 或 `"The Pure Yang Compendium"`，更侧重于其作为一本指导书或汇编的角色。

- 在这里我想强调汇编的含义。

《SRA2Fastq.wdl》
------------------------------------------
随着项目的进展，现在我有了站在更大的舞台的机会。我需要准备一个面向巨量数据的自动化的工具，我需要在WDL（Workflow Description Language，是Broad Institute专门开发用来跑流程的语言）下工作。先期目标是将文件的基本处理放在云平台。

WDL基本元件有5个，分别是定义总流程的`workflow`、定义单个任务的`task`、运行任务的`call`、定义任务中命令的`command`以及输出`output`。
![图片](https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/9ac9c4ad-78c9-4986-ab28-c7ec59b21910)

《SAM2Fastq》
------------------------------------------
实在是缺少必要的工具实现我这样特殊的需求，无奈自己写一个。优化空间蛮大的。
<img width="1178" alt="截屏2024-03-06 23 35 54" src="https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/b420dbba-7266-40cb-ac76-bc2391579fcc">

结果还行，就是python慢了些。
![图片](https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/5a2ee751-1d90-4c2f-b592-8cc508b5ba40)

虽然RG改变的原因不明确，但是至少符合预期。

<img width="657" alt="截屏2024-03-07 13 29 00" src="https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/366c5ef6-617e-46a9-9f3e-ad3155ca365c">

可以是可以了，但是为了满足下游的应用，还是要改改，首先要把reads group整出来，得想想办法把这个信息传入到barcode上，这样我在下游分析的时候，可能可以当作批次来用。

再者，现在这个python脚本的效率太低了，我得整个C的。而且要改一下现在接受文件的变量，让它接受外部输入的文件地址。

结果：C版本的程序的处理速度相当的快，处理5亿条reads的时间从89min减少到了15分钟，速度上还是有潜力可挖的，峰值的磁盘读取只有160MB/S。

《尝试微调一个代码copolit》
------------------------------------------

做点小小的尝试，小而美？用来为微调meta发现的模型以及copliot搜索引擎积累技术


《Allen_Brain_atlas可视化探索》
------------------------------------------
Allen脑科学研究所的单细胞图谱的展示非常快，尝试探究其加载技术有何不同。浏览过程中发现它的加载方式和地图软件很接近，那岂不是正好专业对口？我可是在挂科率极高的测量学和测量学实习都能拿80分手搓遥感地图的男人。顺着这个思路，我寻思allen他们应该也是采取了瓦片的思路，我开始分析XHR传输的文件。果然发现了大量的bin文件在随图像的分级加载在同时传输。于是我尝试获取了所有的bin文件，发现这些文件似乎有数字规律。接着我尝试读取bin文件中的内容，尝试了多种解压方法和读取方案，都不正确。首先我猜测这个是cirro的jsol/json文件，发现无法读取。从js中解析猜测是arraybuffer这种特定的二进制文件，发现也不对，且其各个bin文件头缺乏特定的标识符号信息，可能文件并不是一种特殊的二进制压缩文件。进一步的，我在XHR中发现了一个json文件，名叫scatterbrain.json。名字蛮奇怪的，这是另一个稀疏注意力技术的名字，字面意思为马大哈，无法连续思考的人（[词源](https://www.etymonline.com/cn/word/scatterbrain)）。我打开了json查看，发现json中有明显的注释：points、boundingBox、lx、uy之类的名次，我猜测这是坐标范围。

<img width="444" alt="截屏2024-09-26 10 37 09" src="https://github.com/user-attachments/assets/a9117b32-5fd2-4363-90d6-6d712c5b33b9">

此外，在json的另一部分，可以看到明显的树状结构，我对这里的信息进行了可视化。

<img width="679" alt="截屏2024-09-26 10 37 45" src="https://github.com/user-attachments/assets/47ff2676-e8f2-4126-8a9a-574fb7d970f3">

可视化的结果如下图所示：

<img width="400" alt="截屏2024-09-26 10 39 06" src="https://github.com/user-attachments/assets/334c5a5a-4e57-424d-a46b-bb2ded2f59c7">

到这里，如果我们解析bin文件的结果能够复现出umap图，拿我们就可以确定allen的加速方法了。从JSON的结构来看，bin中应该是坐标信息。我改为data = np.fromfile(filename, dtype=np.float32)来读取数据。我选择了一个numSpecimens为368的bin文件进行读取，发现按照float32的数据类型果然解析出了736（2 * 368）个元素，且每个元素都在JSON的值域定义中。我利用这个方法读取了作为根文件的r.bin，并尝试利用解析出的坐标信息进行绘图。结果和预期一致。（下图中，左侧为bin文件还原出的图像，右侧为allen 在web端展示的图像）
<img width="1606" alt="图片" src="https://github.com/user-attachments/assets/2dcf5fbe-6f4c-4127-b777-ccb703d0f129">

到这里就很明确了，虽然allen网页上写着400万细胞，但是事实上每次只加载十多万个点。接下来就只剩下一个问题了，因为我在使用的时候观察到了瓦片的加载方式，到底allen是不是呢？我设定了统一的画布，把所有的bin都分别绘制。我看到了明显的分块的痕迹。这一点在allenABC_getAllBin.py中可以复现，其分层逻辑与JSON中一致。为了便于展示，我还准备了叠加所有binr0part.py这个脚本，它会把所有的bin绘制到一起，并绘制边框。结果如下图所示。
![overlaid_plot](https://github.com/user-attachments/assets/7d79813b-22c6-4016-99f5-6418c1ca2594)

到此，allen的可视化思路已经完全解析：allen首先对400w细胞进行了降采样，只保留维持umap可视化效果的必要的点；同时，allen这个层级结构表明数据以类似树形的方式组织，只在用户需要的时候加载不同的枝叶，这是在处理大型数据传输/可视化时的典型方式（尤其是测绘领域）。

剩下的就是工程实现上的问题了，这些都有成熟的解决方案，暂且按下不表。
