from __future__ import division
from titlecase import titlecase
import numpy
from uuid import uuid1
class d3object:
    def __init__(self,
                 height=100,
                 width=100,
                 topHtml='',
                 bottomHtml='',
                 style=None,
                 publish=False,
                 test=False,
                 precision=4,
                 d3=None,
                 phantomExec='phantomjs',
                 keepTempDir='',
                 **kw):
        self.id='id-{0}'.format(uuid1())
        self.phantomExec = phantomExec
        self.keepTempDir = keepTempDir
        self.width=width
        self.html='<div id="{0}" class="d3Output"></div>'.format(self.id)
        self.css=[]
        self.varsToPass={'width':width,
                         'height':height,
                         'd3ObjId':self.id,
                         }

        self.precision=precision
        self.js=['''
var None=null;
var inf='Inf.';
function utfDecode(x){
    try{
        var r = /[\\\\]{1,2}u([0-9a-fA-F]{4})/gi;
        var xnew = x.replace(r, function (match, grp) {
            return String.fromCharCode(parseInt(grp, 16));
        });
        xnew  = unescape(xnew);
        return xnew;
    }
    catch(err){
        return x
    }
}
        ''','']

        if style in (None, ''):
            self.html='{0}\n{1}\n{2}'.format(topHtml, self.html, bottomHtml)
        elif style=='JFFigure':
            self.html='\n'.join((self.html,
                                 '''<div class="d3Output description figure" style="width: {0}px">
                                    <b>Figure{1}.{2}</b>{3}</div>
                                  '''
                                     .format(width,
                                             ' '+str(kw['number']) if 'number' in kw else '',
                                             ' '+titlecase(str(kw['title']))+'.' if 'title' in kw else '',
                                             ' '+str(kw['desc']) if 'desc' in kw else '',
                                             ),
                                ))
            self.addCss(self.getStandardCss('jfCss'))
        elif style=='JFTable':
            self.html='\n'.join(('<div class="d3Output header" style="width: {0}px;">Table{1}</div>'
                                    .format(width, ' '+str(kw['number']) if 'number' in kw else ''),
                                 '<div class="d3Output title" style="width: {0}px;">{1}</div>'
                                     .format(width, ' '+titlecase(str(kw['title'])) if 'title' in kw else ''),
                                 '<div class="d3Output description" style="width: {0}px">{1}</div>'
                                     .format(width, ' '+str(kw['desc']) if 'desc' in kw else ''),
                                 self.html,
                                ))
            self.addCss(self.getStandardCss('jfCss'))
        elif style=='JFTableFigure':
            self.html='\n'.join(('<div class="d3Output header" style="width: {0}px;">Figure{1}</div>'
                                    .format(width, ' '+str(kw['number']) if 'number' in kw else ''),
                                 '<div class="d3Output title" style="width: {0}px;">{1}</div>'
                                     .format(width, ' '+titlecase(str(kw['title'])) if 'title' in kw else ''),
                                 '<div class="d3Output description" style="width: {0}px">{1}</div>'
                                     .format(width, ' '+str(kw['desc']) if 'desc' in kw else ''),
                                 self.html,
                                ))
            self.addCss(self.getStandardCss('jfCss'))

        if d3!=None:
            if d3.__class__.__name__=='d3object':
                if d3.css[0]!='\n'+self.getStandardCss('jfCss') or len(d3.css)>1:
                    self.css=list(set(self.css) | set(d3.css))
                d3.addPageBreak()
                self.html='\n'.join((d3.render(mode=('only','html')),self.html))
            else:
                raise TypeError

        self.publish=publish
        if publish:
            from IPython.display import HTML
            html='<style>\n{0}\n</style>\n{1}'.format('\n'.join(self.css), self.html)
            return HTML(html)
            self.html=''

    def removeTestObject(self):
        from IPython.core.display import publish_javascript
        publish_javascript('''$('#d3TestOutput').remove();''')

    def convertVar(self, var):
        typeVar=type(var)
        if str(var)=='nan':
            return None
        elif typeVar==numpy.ndarray:
            return self.convertVar(var.tolist())
        elif typeVar == float or typeVar == numpy.float64:
            return round(var, self.precision)
        elif typeVar == list:
            return [self.convertVar(i) for i in var]
        elif typeVar == dict:
            outTemp={}
            for k in var:
                outTemp[k]=self.convertVar(var[k])
            return outTemp
        elif typeVar in (str, int) or var==None:
            return var
        elif typeVar==long:
            return int(var)
        else:
            print typeVar
            raise TypeError

    def addVar(self, **kw):
        for k in kw:
            self.varsToPass[k]=self.convertVar(kw[k])

    def getJsInputs(self):
        jsInputs=[]
        inputs=self.varsToPass
        for i in inputs:
            outTemp=i+'='
            typeOut=type(inputs[i])
            if typeOut == str:
                outTemp+='"%s"' % inputs[i]
            elif typeOut in (list, dict, int, float) or inputs[i]==None:
                outTemp+=str(inputs[i])
            else:
                print typeOut
                raise TypeError
            jsInputs.append(outTemp)
        jsInputs='\n'.join(['var '+i+';' for i in jsInputs]).replace("u'", "'")
        self.jsInputs=jsInputs

    def addJs(self, jsStr):
        if type(jsStr)!=str:
           raise TypeError
        self.js.append(jsStr)

    def addCss(self, css):
        if type(css)!=str:
           raise TypeError
        if type(css)==list:
            for c in css:
                self.addCss(c)
        else:
            self.css.append('{0}'.format(css))

    def pValsStar(self, dataAdd, index=0):
        if len(dataAdd)==0:
            return
        for i in xrange(len(dataAdd[index])):
            for j in xrange(len(dataAdd[index][0])):
                if type(dataAdd[index][i][j])==str: continue
                x=dataAdd[index][i][j]
                if x<0:        dataAdd[index][i][j]='Error'
                elif x<=0.01:  dataAdd[index][i][j]='&#x2605;&#x2605;&#x2605;'
                elif x<=0.05:  dataAdd[index][i][j]='&#x2605;&#x2605;'
                elif x<=0.1:   dataAdd[index][i][j]='&#x2605;'
                elif x<=1:     dataAdd[index][i][j]=''
                else:          dataAdd[index][i][j]='Error'

    def addPanel(self, title=''):
        html=u'''<div class="figtags panel description" style="width: {0}px">{1}</div>'''.format(self.width, title).replace('\n','')
        self.addJs(''' $("#{0}").append('{html}');'''.format(self.id, html=html))
        return '-tag-{0}'.format(uuid1())

    def getUUID(self, x):
        return '-{1}-{0}'.format(uuid1(), x)

    def addTable(self,
         data=[],
         dataAdd=[],
         pVals=False,
         fontSizeCells=[12,8],
         fontSizeCellsLabels=[16,10],
         sRows=None,
         sColumns=None,
         sRowsMargins=[5],
         sColsMargins=[5],
         varLabels=['Value', 'p-value'],
         fontSizeHeaders=12,
         shrinkHeadersBorders=1.5,
         heatmapIgnoreText=1,
         heatmap={
             'draw':1,
             'spacing':2,
             'fillProportion':5,
             'addText':1,
             'addTextRows':1,
             'addBorders':1,
             'addOutsideBorders':-1,
             'rectWidth':45,
             'rectHeight':45,
        },
        smallHeatmap={
             'draw':1,
             'spacing':0,
             'fillProportion':4,
             'addText':0,
             'addTextRows':0,
             'addBorders':0,
             'addOutsideBorders':-1,
             'rectWidth':4,
             'rectHeight':4,
        },
        heatmapLegendVert=0,
        legend= {
            'draw':1,
            'width':100,
            'height':15,
            'rectWidth':60,
            'rectHeight':60
        },
        rightPaneOffset=100,
        colorDomainMin=False,
        colorDomainMax=False,
        colorDomainSymmetric=False,
        colorDomainAuto=1,
        colorDomainAutoIgnoreColumns=[],
        colorDomainAutoIgnoreRows=[],
        colorDomainIgnoreColumns=[],
        colorDomainIgnoreRows=[],
        colorRange=['#B9FB8A', '#9BF293', '#7EE79D', '#65DCA6', '#51CFAD', '#43C3B1', '#3FB5B3',
                '#43A7B2', '#4C99AD', '#568BA6', '#5F7D9C', '#656F8F', '#696181', '#6A5471',
                '#684861', '#633D51', '#5B3341', '#522A33', '#472226', '#3B1B1A', '#2E1510'],
        barSize=0.6
):
        figTag='-tag-{0}'.format(uuid1())
        if type(pVals)!=bool:
            self.pValsStar(dataAdd, pVals)
        if sRows==None:
            sRows = ['' for _ in data[0]]
        if sColumns==None:
            sColumns = ['' for _ in data]

        if colorRange != None:
            colorDomain=[0,1]
            if colorDomainAuto>0:
                colorRangeData=data
                if len(colorDomainAutoIgnoreColumns)+len(colorDomainAutoIgnoreRows)>0:
                    colorRangeData=[]
                    for i in xrange(len(data)):
                        if i in colorDomainAutoIgnoreRows: continue
                        for j in xrange(len(data[0])):
                            if j in colorDomainAutoIgnoreColumns: continue
                            colorRangeData.append(data[i][j])

                if colorDomainAuto==2:
                    avgRes=numpy.average(colorRangeData)
                    stdRes=numpy.std(colorRangeData, dtype=numpy.float64, ddof=1)
                    nObs=len(colorRangeData)
                    colorDomain=[max(numpy.min(colorRangeData),avgRes-stdRes/nObs*1.96),
                                    min(numpy.max(colorRangeData),avgRes+stdRes/nObs*1.96)]
                if colorDomainAuto==1:
                    colorDomain=[numpy.min(colorRangeData),numpy.max(colorRangeData)]

            if colorDomainSymmetric:
                colorDomain=max(numpy.fabs(colorDomain))
                colorDomain=[-colorDomain, colorDomain]
                colorRange=list(reversed(colorRange))+colorRange[1:]
            if colorDomainMin:
                colorDomain=[colorDomainMin, colorDomain[1]]
            if colorDomainMax:
                colorDomain=[colorDomain[0], colorDomainMax]

            colorRangeLen=len(colorRange)
            colorDomain=(numpy.array([i/colorRangeLen for i in xrange(colorRangeLen+1)])*(colorDomain[1]-colorDomain[0])+colorDomain[0]).tolist()
        else:
            colorDomain=[]
            colorRange=[]

        self.addVar(  figTag=figTag,
                    colorDomain=colorDomain,
                    colorRange=colorRange,
                    data=data,
                    dataAdd=dataAdd,
                    fontSizeCellsLabels=fontSizeCellsLabels,
                    fontSizeCells=fontSizeCells,
                    varLabels=varLabels,
                    sRows=sRows,
                    sColumns=sColumns,
                    heatmapLegendVert=heatmapLegendVert,
                    heatmap=heatmap,
                    smallHeatmap=smallHeatmap,
                    legend=legend,
                    fontSizeHeaders=fontSizeHeaders,
                    heatmapIgnoreText=heatmapIgnoreText,
                    sRowsMargins=sRowsMargins,
                    sColsMargins=sColsMargins,
                    shrinkHeadersBorders=shrinkHeadersBorders,
                    rightPaneOffset=rightPaneOffset,
                    colorDomainIgnoreColumns=colorDomainIgnoreColumns,
                    colorDomainIgnoreRows=colorDomainIgnoreRows,
                    colorDomainMin=colorDomainMin if colorDomainMin else 'false',
                    colorDomainMax=colorDomainMax if colorDomainMax else 'false',
                    barSize=barSize,
                  )
        self.addCss('''
            .heatmapCell path, .heatmapCell line, .heatmapCell polyline, .d3Output polyline {
                fill: none;
                stroke-width: 1px;
                stroke: black;
                shape-rendering: crispEdges !important;
            }
            .heatmapCell text, .heatmapCell rect, .d3Output rect {
                font-size: 1em;
                shape-rendering: crispEdges !important;
            }
        ''')
        self.addCss('#'+figTag+'{shape-rendering: crispEdges !important;}')
        self.addJs('''

        Array.prototype.sum = function() {
          return this.reduce(function(a,b){return a+b;});
        }

        var svg = d3.select("#"+d3ObjId)
                        .append("svg")
                        .attr("width", width)
                        .attr("height", height)
                        .style("border-bottom", "1px solid black")

        var color = d3.scale.linear()
                        .domain(colorDomain)
                        .range(colorRange);

        function getColor(data){
            if(colorDomainMin!='false')
                if(colorDomainMin>data)
                    return color(colorDomainMin);
            if(colorDomainMax!='false')
                if(colorDomainMax<data)
                    return color(colorDomainMax);
            return color(data);

        }
        //_________________________________________________________________________________
        //
        //Heatmap drawing function
        //_________________________________________________________________________________
        function drawHeatmap(data,
                             x,
                             y,
                             spacing,
                             fillProportion,
                             addText,
                             addTextRows,
                             addBorders,
                             addOutsideBorders,
                             rectWidth,
                             rectHeight,
                             svg,
                             objId){

            var heatmap=svg.append("svg")
                          .attr("class", "heatmap")
                          .attr("y", y)
                          .attr("x", x)
                          .attr("id", objId)

            var addLength = dataAdd.length;
            if(heatmapIgnoreText==1)
                var cumulHeight=rectHeight-fontSizeCells.sum()-(addLength+1)*2;
            else
                var cumulHeight=rectHeight-fillProportion-fontSizeCells.sum()-(addLength+1)*2;

            var borderOffset=[0,0];
            if(addOutsideBorders>=0&&objId=='smallHeatmap')
                borderOffset=[addOutsideBorders+1,addOutsideBorders+1];
            var bars = {
                'row': 0,
                'col': 0
            }
            for(var i=0; i<data[0].length; i++){
                if(sColumns[0][i]=='|'){
                    bars.col++;
                }
                bars.row=0;
                for(var j=0; j<data.length; j++){
                    if(sRows[0][j]=='|'){
                        bars.row++;
                        continue
                    }
                    if(sColumns[0][i]=='|'){
                        continue
                    }

                    if(addLength>0){
                        if(dataAdd[0][j][i]=='Error'){ continue; }
                        if(addLength>1){
                            if(dataAdd[1][j][i]=='Error'){ continue; }
                        }
                    }
                    var g=heatmap.append("g")
                            .attr("class", "heatmapCell")
                            .attr("transform", "translate("+ (borderOffset[0]+(i)*(rectWidth+spacing)-bars.col*barSize*rectWidth+addTextRows*(sRowsMargins.sum()+5)) +","
                                                           + (borderOffset[1]+(j)*(rectHeight+spacing)-bars.row*barSize*rectHeight+addTextRows*(sColsMargins.sum()+5)) + ")")
                    if(colorDomainIgnoreRows.indexOf(j)==-1 && colorDomainIgnoreColumns.indexOf(i)==-1)
                        g.append("rect")
                            .attr("y", rectHeight-fillProportion)
                            .attr("fill", getColor(data[j][i]))
                            .attr("id", "heatCell")
                            .attr("width", rectWidth)
                            .attr("height", fillProportion)
                    if(addText||addText==1){
                        g.append("text")
                            .attr("x", rectWidth-5)
                            .attr("y",cumulHeight)
                            .attr("id", "heatText")
                            .attr("dy", fontSizeCells[0]+"px")
                            .style("font-size", fontSizeCells[0]+"px")
                            .attr("text-anchor", "end")
                            .text(data[j][i]);
                        for(var k=0; k<addLength; k++){
                            g.append("text")
                                .attr("x", rectWidth-5)
                                .attr("y", cumulHeight+fontSizeCells.slice(0,k+1).sum()+(k+1)*2)
                                .attr("dy", fontSizeCells[k+1]+"px")
                                .attr("id", "heatTextAdd")
                                .style("font-size", fontSizeCells[k+1]+"px")
                                .attr("text-anchor", "end")
                                .text(dataAdd[k][j][i]);
                        }
                    }
                    if(addBorders||addBorders==1){
                        g.append("polyline")
                            .attr("points", "0,0 "+rectWidth+",0 "+rectWidth+","+rectHeight+" 0,"+rectHeight+" 0,0")
                    }
                }
            }
            if(addOutsideBorders>=0){
                    var box = heatmap.append("rect")
                        .attr("fill", "none")
                        .attr("stroke", "#000")
                        .attr("stroke-widtx", "1px");
                    if(objId=='heatmap')
                        box.attr("x", sRowsMargins.sum()+5-addOutsideBorders)
                           .attr("y", sColsMargins.sum()+5-addOutsideBorders)
                           .attr("width", data[0].length*(spacing+rectWidth)-spacing+2*addOutsideBorders)
                           .attr("height", data.length*(spacing+rectHeight)-spacing+2*addOutsideBorders);
                    else{
                        box.attr("x", 1)
                           .attr("y", 1)
                           .attr("width", data[0].length*(spacing+rectWidth)-spacing+2*addOutsideBorders-1)
                           .attr("height", data.length*(spacing+rectHeight)-spacing+2*addOutsideBorders-1);
                        }
            }
            if(addTextRows||addTextRows==1){
                //Columns
                for(var k=0; k<sColumns.length; k++){
                    var z=0;
                    var bars = 0;
                    for(var i=0; i<data[0].length; i++){
                        if(sColumns[0][i]=='|') bars++;
                        if(sColumns[k][i]==null){
                            z++;
                        }
                        else if(sColumns[k][i]==''||sColumns[0][i]=='|'){
                            z=0;
                        }
                        else{
                            var g=heatmap.append("g")
                                    .attr("class", "heatmapCell")
                                    .attr("transform", "translate("+ ((i-z)*(rectWidth+spacing)+(sRowsMargins.sum()+5)-bars*barSize*rectWidth) +",0)");
                            g.append("text")
                                .attr("x", (rectWidth/2)*(z+1)+z*spacing/2)
                                .attr("y", sColsMargins.sum()-sColsMargins.slice(0,k+1).sum())
                                .style("font-size", fontSizeHeaders+"px")
                                .attr("text-anchor", "middle")
                                .text(sColumns[k][i]);
                            g.append("polyline")
                                    .attr("points", ""+ (0+shrinkHeadersBorders) +","+ (sColsMargins.sum()-sColsMargins.slice(0,k+1).sum()+5) +" "+ (rectWidth*(z+1)+z*spacing-shrinkHeadersBorders) +","                                            +(sColsMargins.sum()-sColsMargins.slice(0,k+1).sum()+5)+"");
                            z=0;
                        }

                  }
                }
                //Rows
                for(var k=0; k<sRows.length; k++){
                    var z=0;
                    var bars = 0;
                    for(var j=0; j<data.length; j++){
                        if(sRows[0][j]=='|') bars++;
                        if(sRows[k][j]==null){
                            z++;
                        }
                        else if(sRows[k][j]==''||sRows[0][j]=='|'){
                            z=0;
                        }
                        else{
                            var g=heatmap.append("g")
                                    .attr("class", "heatmapCell")
                                    .attr("transform", "translate(0,"+ ((j-z)*(rectHeight+spacing)+(sColsMargins.sum()+5)-bars*barSize*rectHeight)+ ")");
                            g.append("text")
                                .attr("x", sRowsMargins.sum()-sRowsMargins.slice(0,k+1).sum())
                                .attr("y", 0.5*(rectHeight*(z+1)+(z)*spacing+fontSizeHeaders))
                                .style("font-size", fontSizeHeaders+"px")
                                .attr("text-anchor", "end")
                                .text(sRows[k][j]);
                            g.append("polyline")
                                .attr("points", ""+ (sRowsMargins.sum()-sRowsMargins.slice(0,k+1).sum()+5) +","+ (0+shrinkHeadersBorders) + " "                                    + (sRowsMargins.sum()-sRowsMargins.slice(0,k+1).sum()+5) +","+ ((z+1)*rectHeight+z*spacing-shrinkHeadersBorders) +"");
                            z=0;
                        }
                    }
                }
            }
        }

        //_________________________________________________________________________________
        //
        //Legend for a heatmap
        //_________________________________________________________________________________
        function drawLegend(legendSize, x, y, tickValues, colorDomain, color, svg){
        var legendcolorRangecale=d3.scale.linear()
                                .domain([0,legendSize[0]])
                                .range([colorDomain[0], colorDomain[colorDomain.length-1]]),
        legendObj=svg.append("svg")
                  //.attr("width", legendSize[0]+legendSize[2])
                  //.attr("height", legendSize[1]+12)
                  .attr("y", y)
                  .attr("x", x)
        for(var i=0; i<=legendSize[0]; i=i+legendSize[2]){
            legendObj.append("rect")
                .attr("x", i-1)
                .attr("fill", color(legendcolorRangecale(i)))
                .attr("width", legendSize[2])
                .attr("height", legendSize[1])
                .attr("transform", "translate(5,0)")
        }

        var legendScale = d3.scale.linear()
                    .domain([colorDomain[0], colorDomain[colorDomain.length-1]])
                    .range([0,legendSize[0]]);

        var legendXAxis = d3.svg.axis()
                        .scale(legendScale)
                        .orient("bottom")
                        .tickSize(0,0,0)
                        .tickValues(tickValues)


        legendObj.append("g")
            .attr('class', 'axis')
            .attr("transform", "translate(5," + legendSize[1] + ")")
            .call(legendXAxis);



        }
        function drawLegendVert(legendSize, x, y, tickValues, colorDomain, color, svg){
        var legendcolorRangecale=d3.scale.linear()
                                .domain([0,legendSize[0]])
                                .range([colorDomain[0], colorDomain[colorDomain.length-1]]),
        legendObj=svg.append("svg")
                  //.attr("width", legendSize[0]+legendSize[2])
                  //.attr("height", legendSize[1]+12)
                  .attr("y", y)
                  .attr("x", x)
                  .attr("id", "vertLegend")
        if(heatmapLegendVert==1)
                  legendObj.style("opacity", 0.01)
        for(var i=0; i<=legendSize[0]; i=i+legendSize[2]){
            legendObj.append("rect")
                .attr("y", i-1)
                .attr("fill", color(legendcolorRangecale(i)))
                .attr("width", legendSize[1])
                .attr("height", legendSize[2])
                .attr("transform", "translate(5,0)")
        }

        var legendScale = d3.scale.linear()
                    .domain([colorDomain[0], colorDomain[colorDomain.length-1]])
                    .range([5,legendSize[0]-5]);

        var legendXAxis = d3.svg.axis()
                        .scale(legendScale)
                        .orient("right")
                        .tickSize(0,0,0)
                        .ticks(5)


        legendObj.append("g")
            .attr('class', 'axis')
            .attr("transform", "translate("+(legendSize[1]*1.5)+"," + (0*legendSize[1]) + ")")
            .call(legendXAxis);



        }
        function drawLegendBox(x, y, rectWidth, rectHeight, svg){
            var legendObj=svg.append("svg")
                      //.attr("width", legendSize[0]+legendSize[2])
                      //.attr("height", legendSize[1]+12)
                      .attr("y", y-rectHeight)
                      .attr("x", x)

            var addLength = dataAdd.length;
            var cumulHeight=fontSizeCellsLabels.sum()+addLength*2;
            var g=legendObj.append("g")
                    .attr("class", "heatmapCell")

            g.append("rect")
                .attr("x", 1)
                .attr("y", rectHeight-heatmap.fillProportion/heatmap.rectHeight*rectHeight)
                .attr("fill", colorRange[0])
                .attr("width", rectWidth-1)
                .attr("height", heatmap.fillProportion/heatmap.rectHeight*rectHeight)

            g.append("text")
                .attr("x", rectWidth-5)
                .attr("y", rectHeight-cumulHeight-5-heatmap.fillProportion)
                .attr("dy", fontSizeCellsLabels[0]+"px")
                .style("font-size", fontSizeCellsLabels[0]+"px")
                .attr("text-anchor", "end")
                .text(varLabels[0]);
            for(var k=0; k<addLength; k++){
                g.append("text")
                    .attr("x", rectWidth-5)
                    .attr("y", rectHeight-5-heatmap.fillProportion-cumulHeight+fontSizeCellsLabels.slice(0,k+1).sum()+(k+1)*2)
                    .attr("dy", fontSizeCellsLabels[k+1]+"px")
                    .style("font-size", fontSizeCellsLabels[k+1]+"px")
                    .attr("text-anchor", "end")
                    .text(varLabels[k+1]);

            }
            g.append("polyline")
                .attr("points", "1,1 "+ (rectWidth-1) +",1 "+ (rectWidth-1) +","+rectHeight+" 1,"+rectHeight+" 1,1")

        }

        var regressionResults=svg.append("g").attr('id', 'svgElement'+d3ObjId+figTag)
        if(heatmap.draw==1){
            drawHeatmap(data/*data*/,
                        0/*x*/,
                        0/*y*/,
                        heatmap.spacing/*spacing*/,
                        heatmap.fillProportion/*fillProportion*/,
                        heatmap.addText/*addText*/,
                        heatmap.addTextRows/*addTextRows*/,
                        heatmap.addBorders/*addBorders*/,
                        heatmap.addOutsideBorders/*addOutsideBorders*/,
                        heatmap.rectWidth/*rectWidth*/,
                        heatmap.rectHeight/*rectHeight*/,
                        regressionResults,/*svg parent*/
                        'heatmap'/*id*/)
            }
        var legendX=Math.round(sRowsMargins.slice(0,sRowsMargins.length-1).sum()/2+data[0].length*(heatmap.rectWidth+heatmap.spacing)+5+rightPaneOffset);
        if(smallHeatmap.draw==1){
            drawHeatmap(data/*data*/,
                        legendX/*x*/,
                        Math.round(heatmap.addTextRows*(sColsMargins.sum()))/*y*/,
                        smallHeatmap.spacing/*spacing*/,
                        smallHeatmap.fillProportion/*fillProportion*/,
                        smallHeatmap.addText/*addText*/,
                        smallHeatmap.addTextRows/*addTextRows*/,
                        smallHeatmap.addBorders/*addBorders*/,
                        smallHeatmap.addOutsideBorders/*addOutsideBorders*/,
                        smallHeatmap.rectWidth/*rectWidth*/,
                        smallHeatmap.rectHeight/*rectHeight*/,
                        regressionResults,/*svg parent*/
                        'smallHeatmap'/*id*/)
        }
        if(legend.draw==1){
            if(smallHeatmap.draw==1){
            drawLegend( [data[0].length*(smallHeatmap.rectWidth+smallHeatmap.spacing)-smallHeatmap.spacing-smallHeatmap.rectWidth,legend.height,1]  /*legendSize*/,
                    Math.round(smallHeatmap.rectWidth/2+legendX-5+ Math.max(0,smallHeatmap.addOutsideBorders ))/*x*/,
                    Math.round((data.length)*(smallHeatmap.rectHeight+smallHeatmap.spacing)+sColsMargins.sum()+legend.height+5+2*Math.max(0,smallHeatmap.addOutsideBorders))/*y*/,
                    [colorDomain[1], colorDomain[colorDomain.length-2]]/*tickValues*/,
                    colorDomain/*colorDomain*/,
                    color/*color*/,
                    regressionResults/*svg*/);
            }
            drawLegendBox(legendX,
                          Math.round((data.length)*(heatmap.rectHeight+heatmap.spacing)+heatmap.spacing+1+sColsMargins.sum()),
                          Math.max(legend.rectWidth, data[0].length*(smallHeatmap.rectWidth+smallHeatmap.spacing)-smallHeatmap.spacing+Math.max(0,2*smallHeatmap.addOutsideBorders)),
                          legend.rectHeight,
                          regressionResults)
        }
        if(heatmapLegendVert==1||heatmapLegendVert==2)
            drawLegendVert( [data.length*(heatmap.rectHeight+heatmap.spacing),legend.height,1]  /*legendSize*/,
                    sRowsMargins.slice(0,sRowsMargins.length ).sum()+data[0].length*(heatmap.rectWidth+heatmap.spacing)+25/*x*/,
                    sColsMargins.sum()+5/*y*/,
                    [colorDomain[1], colorDomain[colorDomain.length-2]]/*tickValues*/,
                    colorDomain/*colorDomain*/,
                    color/*color*/,
                    regressionResults/*svg*/);

        var boundingRect=document.getElementById('svgElement'+d3ObjId+figTag).getBoundingClientRect();
        var boundingRectParent=$(document.getElementById('svgElement'+d3ObjId+figTag)).parent()[0].getBoundingClientRect();
        regressionResults.attr("transform", "translate("+ ((width-boundingRect.width)/2-boundingRectParent.left) +","+ ((height-boundingRect.height)/2+boundingRectParent.top-boundingRect.top) + ")")

        ''')

    def getPhantomJsScript(self, mode, renderTime=1000):
        if 'html' in mode:
            phantomJs='''
                var page = require('webpage').create(),
                    system = require('system'),
                    address, elementHtml;

                address = system.args[1];
                page.viewportSize = { width: 600, height: 600 };

                page.open(address, function (status) {
                    if (status !== 'success') {
                        console.log('Unable to load the address!');
                    } else {
                        window.setTimeout(function () {
                            elementHtml=page.evaluate(function() {
                                document.body.bgColor = 'white';
                                return document.getElementById("d3OutputOutterContainer").innerHTML;
                            });
                            console.log(elementHtml);
                            phantom.exit(1);
                        }, %s);
                    }
                });
            ''' % (renderTime)
        elif 'png' in mode:
            phantomJs='''
                var page = require('webpage').create(),
                    system = require('system'),
                    address, elementHtml;

                address = system.args[1];
                page.viewportSize = { width: 1, height: 1 };

                page.open(address, function (status) {
                    if (status !== 'success') {
                        console.log('Unable to load the address!');
                    } else {
                        window.setTimeout(function () {
                            console.log(page.renderBase64('PNG'));
                            phantom.exit(1);
                        }, %s);
                    }
                });
            ''' % (renderTime)
        return phantomJs

    def render(self, mode=['html'], fileName=None, renderTime=1000):
        if type(mode) not in (list, tuple):
            mode=(mode,)
        self.getJsInputs()
        html=['<style>',
              '\n'.join(self.css),
              '</style>',
              '</head>',
              '<body>',
              '<div id="d3OutputOutterContainer">',
              self.html,
              '</div>',
              '<script>',
              self.js[0],
              self.jsInputs,] + self.js[1:] + ['</script>'
              ]
        if self.publish:
            html='\n'.join(html)
            from IPython.display import HTML
            return HTML(html)

        import tempfile
        from os import unlink
        import subprocess
        from time import sleep

        html=['<html>',
              '<head>',
              '<title></title>',
              '<script src="http://code.jquery.com/jquery-1.8.3.min.js"></script>',
              '<script src="http://d3js.org/d3.v3.min.js"></script>',] +\
              html +\
              ['</body>',
              '</html>',]
        html='\n'.join(html)

        if 'keepTemp' not in mode:
            tempJs=tempfile.NamedTemporaryFile(mode="w+b", delete=False, suffix='.js')
            temp=tempfile.NamedTemporaryFile(mode="w+b", delete=False, suffix='.htm')
        else:
            tempJs=open(self.keepTempDir+'//ipyD3_temp.js', "wb")
            temp=open(self.keepTempDir+'//ipyD3_temp.htm', "wb")

        tempJs.write(self.getPhantomJsScript(mode, renderTime))
        temp.write(html)

        if 'keepTemp' not in mode:
            temp.flush()
            tempJs.flush()
            tempJs.close()
            temp.close()
            phantomJsArgs = (self.phantomExec, tempJs.name, temp.name)
        else:
            tempJs.close()
            temp.close()
            phantomJsArgs = (self.phantomExec, self.keepTempDir+'//ipyD3_temp.js', self.keepTempDir+'//ipyD3_temp.htm')

        phantomJsProc = subprocess.Popen( phantomJsArgs,  stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        html = ''
        err = ''
        while phantomJsProc.poll() is None:
            sleep( 0.1 )
            html, err = phantomJsProc.communicate()
        if 'keepTemp' not in mode:
            unlink(temp.name)
            unlink(tempJs.name)

        if 'html' in mode:
            html=html.replace("&amp;", "&").replace("use href=", "use xlink:href=")
            if 'only' in mode:
                return html
            if 'file'in mode and fileName!=None:
                html=['<html>',
                      '<head>',
                      '</head>',
                      '<style>',
                      '\n'.join(self.css),
                      '</style>',
                      html,
                      '</body>',
                      '</html>',]
                fileOpen=open(fileName,'wb')
                fileOpen.write('\n'.join(html))
                fileOpen.close()
                return True
            html='\n'.join(['<style>','\n'.join(self.css),'</style>'])+html
            if 'show'in mode:
                from IPython.display import HTML
                return HTML(html)
            return html
        elif 'png' in mode:
            if 'only' in mode:
                return html
            if 'file'in mode and fileName!=None:
                fileOpen=open(fileName,'wb')
                fileOpen.write(html)
                fileOpen.close()
                return True
            if 'show'in mode:
                from IPython.display import Image
                return Image(data=html)
            return html

    def addSimpleTable(self,
                 data,
                 dataAdd=[],
                 pVals=False,
                 fontSizeCells=[],
                 sRows=[],
                 sColumns=[],
                 sRowsMargins=[5,100],
                 sColsMargins=[5,20],
                 fontSizeHeaders=9,
                 shrinkHeadersBorders=1.5,
                 spacing=0,
                 addBorders=1,
                 addOutsideBorders=-1,
                 rectWidth=45,
                 rectHeight=0,
                 barSize=0.6,
                 colorRange=None,
                 varLabels=[],

                 ):
        if len(fontSizeCells)==0:
            fontSizeCells=[12]*(1+len(dataAdd))
        self.addTable(data=data,
                 dataAdd=dataAdd,
                 pVals=pVals,
                 fontSizeCells=fontSizeCells+[5],
                 fontSizeCellsLabels=fontSizeCells+[5],
                 sRows=sRows,
                 sColumns=sColumns,
                 sRowsMargins=sRowsMargins,
                 sColsMargins=sColsMargins,
                 varLabels=varLabels,
                 fontSizeHeaders=fontSizeHeaders,
                 shrinkHeadersBorders=shrinkHeadersBorders,
                 heatmapIgnoreText=1,
                 heatmap={
                     'draw':1,
                     'spacing':spacing,
                     'fillProportion':0,
                     'addText':1,
                     'addTextRows':1,
                     'addBorders':addBorders,
                     'addOutsideBorders':addOutsideBorders,
                     'rectWidth':rectWidth,
                     'rectHeight':rectHeight if rectHeight>0 else int(sum(fontSizeCells)+10+2*len(dataAdd)),
                },
                smallHeatmap={
                     'draw':0,
                     'spacing':0,
                     'fillProportion':4,
                     'addText':0,
                     'addTextRows':0,
                     'addBorders':0,
                     'addOutsideBorders':-1,
                     'rectWidth':4,
                     'rectHeight':4,
                },
                legend= {
                    'draw':min(len(varLabels),1),
                    'rectWidth': rectWidth,
                     'rectHeight':rectHeight if rectHeight>0 else int(sum(fontSizeCells)+10+2*len(dataAdd)),
                },
                rightPaneOffset=min(len(varLabels),1)*120,
                colorRange=colorRange,
                barSize=barSize
        )

    def addPageBreak(self):
        self.addJs('''$("#"+d3ObjId).append('<div style="page-break-after:always; display:block; width:1px; height:1px;">&nbsp;</div>')''')

    def getStandardCss(self, mode='jfCss'):
        if mode=='jfCss':
            return'''
                    body{
                        font-family: "Lucinda Grande", "Lucinda Sans Unicode", Helvetica, Arial, Verdana, sans-serif;
                    }
                    .d3Output{
                        min-height: 1.2em;
                        line-height: 1.2em;
                        position: relative;
                        font-size: 1em;
                        padding: 5px 0;

                        list-style: none;
                        background: #fff;
                        color: #000;
                    }
                    svg{
                        color-rendering: optimizeQuality !important;
                        shape-rendering: geometricPrecision !important;
                        text-rendering: geometricPrecision !important;
                    }
                    .d3Output.header{
                        text-align: center;
                        font-weight: bold;
                        border-bottom: none;
                        font-size: 0.9em;

                    }
                    .d3Output.title{
                        text-align: center;
                        font-weight: bold;
                        border-bottom: none;
                        font-size: 1.2em;

                    }
                    .d3Output .description, .d3Output.description{
                        font-size: 0.8em;
                        text-align:justify;
                        text-justify:inter-word;
                        border-bottom: 1px solid #000;
                    }
                    .d3Output .panel{
                        text-align: center !important;
                        page-break-after:avoid;
                    }
                    svg, canvas {
                        border-bottom: 1px solid #000;
                        display: block;
                        margin: 5px 0;
                    }
                    .d3Output.description.figure{
                        border-bottom: none;
                    }
                    '''