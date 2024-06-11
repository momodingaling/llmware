
""" This example shows how to use the slim-qa-gen models to automatically generate a question and answer based on a
context passage.

    There are two 'qa-gen' models - (a) tiny-llama base (1.1b), and (b) phi-3 base (3.8b)

    Both models work the same way with tiny-llama a little faster, and phi-3 a little higher quality.

    The models come packaged both as pytorch and gguf - for most inference use cases, we would recommend
    the gguf versions which are considerably faster.

    This example uses an earnings_release test set that was also included in using_slim_extract_model.py, primarily
    because it generates an interesting set of questions and answers.  Feel free to substitute your own source
    test sets.

    In the example, we will show how to take the generated question-answer pairs and create a mini self-supervised
    instruct dataset.

    models in catalog:

        -- "slim-qa-gen-phi-3"
        -- "slim-qa-gen-phi-3-tool"
        -- "slim-qa-gen-tiny"
        -- "slim-qa-gen-tiny-tool"

    """

import json
import os
import random

from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs
from llmware.configs import LLMWareConfig


def earning_releases_test_set():

    earnings_releases = [

        {"context": "Adobe shares tumbled as much as 11% in extended trading Thursday after the design software maker "
                    "issued strong fiscal first-quarter results but came up slightly short on quarterly revenue guidance. "
                    "Here’s how the company did, compared with estimates from analysts polled by LSEG, formerly known as Refinitiv: "
                    "Earnings per share: $4.48 adjusted vs. $4.38 expected Revenue: $5.18 billion vs. $5.14 billion expected "
                    "Adobe’s revenue grew 11% year over year in the quarter, which ended March 1, according to a statement. "
                    "Net income decreased to $620 million, or $1.36 per share, from $1.25 billion, or $2.71 per share, "
                    "in the same quarter a year ago. During the quarter, Adobe abandoned its $20 billion acquisition of "
                    "design software startup Figma after U.K. regulators found competitive concerns. The company paid "
                    "Figma a $1 billion termination fee."},

        {
            "context": "Dick’s Sporting Goods raised its dividend by 10% on Thursday as the company posted its largest sales "
                       "quarter in its history and projected another year of growth. The company’s shares jumped more than "
                       "15% in intraday trading. CEO Lauren Hobart said on an earnings call Thursday that Dick’s sales "
                       "growth came from bigger tickets — either higher prices or more expensive items — as its transactions "
                       "were flat. Many retailers benefited from a 53rd week in fiscal 2023, but Dick’s said it still broke "
                       "records during its fiscal fourth quarter even without those extra days. Here’s how the athletic "
                       "apparel retailer did compared with what Wall Street was anticipating, based on a survey of "
                       "analysts by LSEG, formerly known as Refinitiv: Earnings per share: $3.85 adjusted vs. $3.35 expected "
                       "Revenue: $3.88 billion vs. $3.80 billion expected The company’s reported net income for the three-month "
                       "period that ended Feb. 3 was $296 million, or $3.57 per share, compared with $236 million, or $2.60 a "
                       "share, a year earlier. Excluding one-time items related to impairment charges and inventory write-offs, "
                       "Dick’s reported earnings per share of $3.85. Sales rose to $3.88 billion, up about 8% from $3.60 billion "
                       "a year earlier. “With our industry-leading assortment and strong execution, we capped off the year "
                       "with an incredibly strong fourth quarter and holiday season,” Hobart said in a statement. “We are "
                       "guiding to another strong year in 2024. We plan to grow both our sales and earnings through "
                       "positive comps, higher merchandise margin and productivity gains,” she added. During the quarter, "
                       "same-store sales rose 2.8%, well ahead of the 0.8% lift that analysts had expected, according to "
                       "StreetAccount. “Growth in transactions” and market share gains drove the increase, said Executive "
                       "Chairman Ed Stack."},

        {"context": "Comcast topped both revenue and profit estimates in the fourth quarter as it lost fewer broadband "
                    "subscribers than expected, and it raised its dividend 7%, the company said Thursday. "
                    "Here’s how Comcast performed, compared with estimates from analysts surveyed by LSEG, "
                    "formerly known as Refinitiv.  Earnings per share: 84 cents adjusted vs. 79 cents expected  "
                    "Revenue: $31.25 billion vs. $30.51 billion expected For the quarter ended Dec. 31, net "
                    "income rose 7.8% to $3.26 billion, or 81 cents a share, compared with $3.02 billion, or "
                    "70 cents a share, a year earlier. Revenue increased 2.3% compared with the prior-year period. "
                    "Adjusted earnings before interest, taxes, depreciation and amortization (EBITDA) was flat year "
                    "over year at about $8 billion.   'For the third consecutive year, we generated the highest revenue, "
                    "adjusted EBITDA and adjusted EPS in our company’s history', Comcast Chief Executive Officer Brian "
                    "Roberts said in a statement. 'We also reported the highest adjusted EBITDA on record at Theme Parks; "
                    "were the #1 studio in worldwide box office for the first time since 2015; and maintained Peacock’s "
                    "position as the fastest growing streamer in the U.S.'"},

        {"context": "Dollar General forecast annual sales above Wall Street estimates on Thursday, banking on higher "
                    "demand from inflation-hit customers buying groceries and essentials from the discount retailer’s stores.  "
                    "Shares of the company rose about 6% in early trading, after falling nearly 45% in 2023 on rising costs "
                    "and stiff competition from bigger retailers. But higher prices and borrowing costs have prompted "
                    "budget-conscious consumers to cook more meals at home, helping Dollar General record stronger "
                    "footfall at its outlets as shoppers hunt for lower-margin, needs-based goods, over pricier general "
                    "merchandise. “With customer traffic growth and market share gains during the quarter, we believe our "
                    "actions are resonating with customers,” CEO Todd Vasos said in a statement. Vasos’s strategy - to focus "
                    "on the basics, like more employee presence at stores, greater customer engagement and expanding "
                    "private-label brands - has helped stabilize Dollar General’s business. Over the last few quarters, "
                    "Dollar General and rival Dollar Tree have struggled with rising costs linked to their supply "
                    "chains, labor and raw materials, while facing tough competition from retailers like Walmart "
                    "and Chinese ecommerce platform Temu. Dollar Tree’s shares fell more than 15% on Wednesday, after it "
                    "forecast weak sales and profit for 2024 and laid out plans to shutter 970 of its Family Dollar "
                    "stores. “Dollar General has a much rosier outlook than Dollar Tree... Dollar Tree’s challenges "
                    "with Family Dollar were years in the making, while Dollar General has embarked on an aggressive "
                    "effort to add more frozen, refrigerated and fresh produce,” eMarketer senior analyst Zak Stambor said.  "
                    "Dollar General forecast 2024 sales to grow between 6.0% and 6.7%, above analysts’ estimate of 4.4% "
                    "growth to $40.33 billion, according to LSEG data. It still sees annual per-share profit between "
                    "$6.80 and $7.55, compared with estimates of $7.55.  Its fourth-quarter net sales of $9.86 billion "
                    "surpassed estimates of $9.78 billion. It also reported an estimate-beating profit of $1.83 per share."},

        {
            "context": "Shares of Zara owner Inditex hit record highs on Wednesday according to LSEG data, climbing over 6% during "
                       "intraday trading after the company announced its 2023 full-year results. As of 11:50 London time, shared "
                       "were just over 6% higher at 43.58 euros, or $47.69.  Sales increased 10.4% to 35.9 billion euros for the "
                       "year, the company said, signaling this was a record high. Sales grew across all geographic regions and "
                       "across Inditex’s brands and were “very satisfactory,” both online and in store, the company said. A total of "
                       "5,692 stores were operational at the end of the year, Inditex said, adding it plans to expand further in "
                       "2024, including with Zara shops in Los Angeles and Las Vegas. The company also plans to open new distribution "
                       "centers in 2024 and 2025, as part of a major logistics expansion plan that will cost the company "
                       "investments of 900 million euros in both years.  Net income also reached a fresh high after soaring "
                       "30.3% from 2022 to reach 5.4 billion euros last year. The company’s gross profit came in at 20.8 billion "
                       "euros, up 11.9% on the year. “Inditex’s performance in 2023 has been excellent. Our teams have been able to "
                       "take advantage of the opportunities to keep growing profitably. We are investing to drive future growth and "
                       "continue to offer an attractive remuneration to shareholders,” Inditex CEO Oscar García Maceiras said in a "
                       "statement. The Spanish clothing company owns a range of vastly popular brands including household name "
                       "Zara, as well as Pull & Bear, Bershka, Stradivarius, premium retailer Massimo Dutti and sports and the "
                       "athleisure-focused Oysho. Zara, including the Zara Home range, was the biggest contributor to sales in "
                       "2023, followed by Pull & Bear and Massimo Dutti, Inditex said Wednesday.  The company also indicated "
                       "that 2024 was off to a strong start, with sales in constant currency up 11% over the Feb. 1 to March 11 "
                       "stretch, compared with the same period a year earlier."},

        {
            "context": "Oracle reported quarterly earnings on Monday that exceeded Wall Street’s expectations. Shares rose "
                       "13% in extended trading.  Here’s how the company did in the fiscal third quarter ending Feb. 29, compared "
                       "to estimates by LSEG, formerly known as Refinitiv:  Earnings per share: $1.41 adjusted vs. $1.38 expected "
                       "Revenue: $13.28 billion vs. $13.3 billion expected For the fiscal fourth quarter, Oracle said it expects "
                       "earnings of $1.62 to $1.66 per share. Analysts were expecting $1.64 in adjusted earnings per share, according "
                       "to LSEG. Revenue growth will be between 4% and 6% over sales of $13.8 billion a year ago. The midpoint of that "
                       "range would equal revenue of about $14.5 billion, while analysts were expecting a little more than $14.7 billion.  "
                       "Oracle CEO Safra Catz said the company was committed to hitting previously stated goals of $65 billion in "
                       "sales by fiscal 2026. “Some of these goals might prove to be too conservative given our momentum,” Catz said.  "
                       "Revenue rose 7% in the quarter from $12.4 billion a year earlier. Net income climbed 27% to $2.4 billion, "
                       "or 85 cents per share, from $1.9 billion, or 68 cents per share, a year ago.  Oracle’s cloud services and "
                       "license support segment, its largest business, saw sales rise 12% to $9.96 billion, slightly beating "
                       "StreetAccount consensus expectations of $9.94 billion. The company attributed the rise to strong demand "
                       "for its artificial intelligence servers.  Catz said the company added several “large new cloud "
                       "infrastructure” contracts during the quarter. The company’s cloud revenue, which is reported as part "
                       "of the cloud services unit, rose 25% year over year to $5.1 billion, Oracle said. “We signed several large "
                       "deals this quarter and we have many more in the pipeline,” Catz told investors on the earnings call. "
                       "Oracle Chairman Larry Ellison cited increased business from Microsoft on the earnings call. "
                       "“We’re building 20 data centers from Microsoft and Azure. They just ordered three more data centers "
                       "this week,” Ellison said.  The company’s other units didn’t fare as well. Cloud license and on-premise sales "
                       "declined 3% to $1.26 billion, slightly beating StreetAccount’s forecast. Hardware revenue fell 7% to "
                       "$754 million, while sales in the company’s services division slid 5% to $1.31 billion, both falling short "
                       "of StreetAccount expectations.  Prior to Monday’s report, Oracle shares were up 8.7% for the year, "
                       "slightly outperforming the S&P 500."},

        {
            "context": "Porsche on Tuesday warned that profitability will decline this year as it launches new models amid "
                       "tough economic conditions, but hiked its dividend on the back of a rise in 2023 operating profit. The German "
                       "luxury automaker said it expects an operating return on sales of between 15% and 17% in 2024, down from the "
                       "18% margin notched in 2023 and 2022. In the long term, the group targets an operating return on sales of more "
                       "than 20%. Explaining the more cautious profitability outlook, the company cited “the comprehensive renewal "
                       "of its product range in 2024, the global framework conditions, higher depreciations on capitalized "
                       "development costs and the continued investments in the brand and the Porsche ecosystem.” The company’s shares "
                       "were around 4.8% higher by early afternoon, having reversed opening losses of more than 2%. Porsche is "
                       "launching four new car ranges in 2024 in the form of the Panamera, Macan, Taycan and 911 model lines. "
                       "Porsche CFO: Expect significant growth in high-net-worth individuals in China WATCH NOW VIDEO 03:17 "
                       "Porsche CFO: Expect significant growth in high-net-worth individuals in China “2024 is going to be a year of "
                       "product launches for Porsche – more so than any year in our history,” Chairman Oliver Blume said in a "
                       "statement. “We will be introducing a variety of exhilarating sports cars to the road, they will delight "
                       "our customers around the world. This will put the wind at our back for years to come.”"},

        {
            "context": "Lego on Tuesday reported its full-year 2023 results, saying it’s revenue grew by 2% throughout the year, "
                       "in line with expectations. The company made “very, very strong progress” and “grew comfortably” in the "
                       "U.S., its CEO Niels Christiansen told CNBC.  The toy industry has been struggling to maintain "
                       "pandemic-era growth as inflation is putting pressure on demand and sales. In-store participation is greater "
                       "than prior to the pandemic, Lego CEO says In-store participation is greater than prior "
                       "to the pandemic, Lego CEO says The chief executive of Denmark’s Lego on Tuesday reflected on a tough year "
                       "for the world’s largest toymaker, and outlined the firm’s long-term plans to stay relevant and “cool with kids. ”"
                       "Lego said its 2023 revenue was 2% higher compared to the previous year, growing to 65.9 billion Danish krone "
                       "(around $9.65 billion). This was in line with expectations, Lego said in a statement. “It was a difficult year,” "
                       "Lego CEO Niels Christiansen told CNBC. However, he said the company had “managed to take quite a bit of "
                       "market share.” The Danish toymaker said operating profit declined slightly from 17.9 billion Danish krone "
                       "to 17.1 billion, noting that it had boosted spending on strategic initiatives designed to drive growth. "
                       "Net profit came in at 13.1 billion Danish krone in 2023, compared to 13.8 billion the previous year. "
                       "Consumer sales were up 4% despite slumping in China, Lego said, attributing the growth to increasing demand "
                       "in the U.S. and central and eastern Europe. It comes as the wider toy industry has been struggling to "
                       "maintain growth after booming during the coronavirus pandemic, when parents looked for new ways to "
                       "entertain their children and adults re-discovered childhood pastimes.  Toy company Hasbro earlier this month "
                       "said its 2023 revenue fell by 15% compared to 2022 and that it expected to see a further decline this year."},

        {
            "context": "Adidas on Wednesday warned of a sales decline in its overstocked North American market in 2024, as the "
                       "German sportswear brand continues to sell off its remaining Yeezy inventory. Currency-neutral sales in "
                       "North America are expected to decline to a mid-single-digit rate in 2024, but are projected to notch "
                       "mid-single-digit growth worldwide despite persistent “macroeconomic challenges and geopolitical tensions,” "
                       "the company said. Adidas confirmed its 2023 operating profit came in at 268 million euros ($292.9 million) "
                       "on the back of flat currency-neutral sales, significantly above prior expectations as the company continues "
                       "to take a hit from the cessation of its line of Yeezy — footwear the retailer produced in a collaboration with "
                       "American rapper Ye, formerly known as Kanye West. For the fourth quarter, the company posted an operating "
                       "loss of 377 million euros. The board proposed a flat dividend of 0.70 euros per share. “Although by far not "
                       "good enough, 2023 ended better than what I had expected at the beginning of the year,” CEO Bjørn Gulden "
                       "said in a statement. “Despite losing a lot of Yeezy revenue and a very conservative sell-in strategy, "
                       "we managed to have flat revenues. We expected to have a substantial negative operating result, but "
                       "achieved an operating profit of €268 million.” Adidas was confirming preliminary results released in late "
                       "January, when it announced that it would not write off the majority of its Yeezy inventory and would instead "
                       "sell off the remaining shoes at cost. The sportswear giant was forced to axe the Yeezy line after terminating "
                       "its partnership with Ye over a string of anti-Semitic remarks that the rapper made in 2022. Adidas said the "
                       "discontinuation of Yeezy represented a drag of around 500 million euros in the year-on-year comparison "
                       "through 2023, though the sale of parts of the remaining inventory in the second and third quarter positively "
                       "impacted net sales by around 750 million euros. “With a very disciplined go-to-market and buying process, "
                       "we reduced our inventories by almost €1.5 billion. With the exception of the U.S., we now have healthy "
                       "inventories everywhere,” Gulden said. He added that the company is expecting some growth in the "
                       "first quarter of 2024 and a further pick-up in the second half of the year. “We still have a lot of work "
                       "to do, but I feel very confident we are on the right track. We will bring adidas back again. Give us some "
                       "time and we will again say – we got this!” he said. Adidas projected an operating profit of around "
                       "500 million euros in 2024, with unfavorable currency effects expected to “weigh significantly on the "
                       "company’s profitability” because of adverse impacts on both reported revenues and gross margin development."
                       "Adidas shares were flat by mid-morning on Wednesday. Mamta Valechha, equity research analyst at "
                       "Quilter Cheviot, said that, given that the headline numbers were already pre-released in January, the most "
                       "interesting aspect of Wednesday’s report was the “clear acceleration of the Adidas brand.”"},

        {
            "context": "Costco on Thursday missed Wall Street’s revenue expectations for its holiday quarter, despite reporting "
                       "year-over-year sales growth and strong e-commerce gains. Shares of the retailer fell about 4% in aftermarket "
                       "trading. The company’s stock had hit a 52-week high earlier in the day. Here’s what Costco reported for its "
                       "fiscal second quarter of 2024 compared with what Wall Street was expecting, based on a survey of analysts by "
                       "LSEG, formerly known as Refinitiv: Earnings per share: $3.92 vs. $3.62 expected Revenue: $58.44 billion vs. "
                       "$59.16 billion expected In the three-month period that ended Feb. 18, Costco’s net income rose to "
                       "$1.74 billion, or $3.92 per share, compared with $1.47 billion, or $3.30 per share, a year earlier. "
                       "Costco’s revenue for the quarter increased from $55.27 billion in the year-ago period. Comparable sales for "
                       "the company increased 5.6% year over year and 4.3% in the U.S. Excluding changes in gas prices and foreign "
                       "currency, the metric increased 5.8% overall and 4.8% in the U.S. Sales of food and sundries, a category "
                       "that includes snack foods and beverages, were up by mid single digits in the quarter, CFO Richard Galanti "
                       "said on the company’s earnings call. Fresh foods were up high single digits and nonfoods were up mid single "
                       "digits. Ancillary businesses, which includes more service-related purchases like travel, were up by low "
                       "single digits, he said. Costco’s food court, pharmacy and optical centers were top performers in the quarter "
                       "and gas was down low single digits as the price per gallon fell. More shoppers came to Costco, and they "
                       "spent more on their shopping trips during the quarter. Traffic increased 5.3% across the globe and 4.3% in "
                       "the U.S., Galanti said on the earnings call. The average ticket increased in the U.S. and worldwide, he "
                       "said. Inflation was roughly flat year over year in the quarter, which allowed the retailer to reduce "
                       "prices for some items, Galanti said. For example, he said, it’s been able to cut the price of reading "
                       "glasses from $18.99 to $16.99 and slash the price of a 48 count of Kirkland Signature batteries from "
                       "$17.99 to $15.99. In the prior quarter, he said inflation was as much as 1% year over year. Galanti said many "
                       "new items in categories like sporting goods and lawn and garden will also have lower prices compared with "
                       "a year ago because of falling freight and commodity costs. Costco has 875 warehouses, including 603 in "
                       "the U.S. and Puerto Rico. It also has clubs in about a dozen other countries, including Canada, Mexico, "
                       "Japan and China. In the second quarter, Costco opened four new clubs, including three in the U.S. "
                       "and one in Shenzhen, China. That marked its sixth club to open in China, Galanti said. Two of the three "
                       "new U.S. locations were Costco Business Centers, which are specifically geared toward small business "
                       "owners like restaurant operators. As of Thursday’s close, Costco shares have risen nearly 19% since the "
                       "start of the year. The stock touched a 52-week high of $787.08 earlier in the day and closed at $785.59, "
                       "bringing the company’s market value to nearly $350 billion."},

        {
            "context": "Shares of Teleperformance plunged 23% on Thursday, after the French call center and office services group "
                       "missed its full-year revenue target and flagged a “volatile economic environment.” Investors have been "
                       "spooked by the potential impact of artificial intelligence on its business model, as companies become more "
                       "able to tap into the technology directly for their own benefit. Teleperformance shares dropped 16% last "
                       "week, according to LSEG data, after Swedish financial services company Klarna said its Open AI-powered "
                       "customer service assistant was handling two-thirds of customer service calls.  But Teleperformance CEO "
                       "Daniel Julien on Thursday said that AI would be a positive for its business model — and that it will never "
                       "fully replace the value of human interaction. “AI is part of the solutions we provide to the clients,” "
                       "Julien told CNBC’s “Squawk Box Europe.” “AI helps to increase the accuracy of our employees ... which is "
                       "great, but at the end of the day we are here to reduce the friction between the citizens, or the customer, "
                       "and the companies they have bought a product and service from.” He stressed, “It’s not just a transactional "
                       "relationship, it has a lot to do with reassuring, with trust, with empathy. So we perceive AI as enhancing "
                       "the job that our human employees do, but absolutely not replacing them.” hide content Teleperformance SE "
                       "RT Quote | Exchange | EUR 87.16 quote price arrow up+0.68 (+0.79%) Last | 03/15/24 CET WATCHLIST + QUOTE DETAILS "
                       "Teleperformance share price. Teleperformance reported 2.3% higher revenue at 8.345 billion euros "
                       "($9.091 billion) in 2023, as net profit fell year-on-year from 643 million euros to 602 million euros. "
                       "Diluted earnings per share hit 10.18 euros, down from 10.77 euros. In its results, the company said it is "
                       "working with clients on 250 AI projects, including in generative AI, and it has expanded its portfolio "
                       "with new partnerships in the space. “Even the most high-tech or the most AI-involved companies are clients "
                       "of Teleperformance. We chose that there is a complementarity and not separation,” Julien told CNBC, "
                       "flagging the company’s agreement with tech giant and major AI player Microsoft. “They are there to provide "
                       "a solution that is going to augment the productivity, augment the quality of the information that can be "
                       "given to the customer, but, at the end of the day, the customer is a human being. The day the customer is "
                       "going to be a robot, maybe AI will replace the humans.”"},

        {"context": "CrowdStrike shares surged as much as 21% in after-hours trading Tuesday after the cybersecurity "
                    "company reported a beat on the top and bottom lines, plus issued stronger-than-expected guidance for "
                    "the upcoming quarter and full year. Here’s how the company did compared to consensus estimates "
                    "based on a survey of analysts by LSEG, formerly known as Refinitiv: Earnings per share: 95 cents "
                    "adjusted vs. 82 cents expected Revenue: $845 million vs. $839 million expected For the period that "
                    "ended Jan. 31, CrowdStrike saw net income of $54 million, or 22 cents per share, from a "
                    "$48 million loss, or a 20 cent loss per share, in the year-ago period. CrowdStrike has now "
                    "reported GAAP net income for the past four quarters, Chief Financial Officer Burt Podbere "
                    "said in the earnings release. Full-year revenue rose 36% year over year, from $2.24 billion "
                    "to $3 billion. The company also announced it would acquire Flow Security for an undisclosed "
                    "price in a cash-and-stock deal, slated to close in the company’s fiscal first quarter. "
                    "The company has been stepping up its merger and acquisition activity in recent months. “CrowdStrike "
                    "is cybersecurity’s consolidator of choice, innovator of choice, and platform of choice to "
                    "stop breaches,” co-founder and CEO George Kurtz said in a release. The company also guided to "
                    "fiscal first-quarter revenue between $902 million and $906 million, better than a consensus "
                    "estimate of $899 million. CrowdStrike also expects earnings per share for the period between "
                    "89 cents and 90 cents, better than the consensus estimate of 82 cents. Podbere also reiterated "
                    "the company’s focus on achieving $10 billion in annual recurring revenue by 2030. The company "
                    "reached $3.4 billion in annual recurring revenue in January."},

        {"context": "Shares of Amer Sports, the maker of Wilson tennis rackets and Lousiville Slugger baseball "
                    "bats, fell on Tuesday after the company reported strong sales in China but a slowdown in "
                    "wholesale orders. Here’s how the newly public athletic company did in its fourth quarter. "
                    "CNBC didn’t compare the results to Wall Street estimates because it’s the first earnings "
                    "report since Amer Sports went public. Loss per share: 25 cents Revenue: $1.32 billion In the "
                    "three months ended Dec. 31, the company reported a net loss of $94.9 million, or 25 cents "
                    "per share, compared with $148.3 million, or 39 cents per share, a year earlier. Sales rose to "
                    "$1.32 billion, up about 10% from $1.2 billion a year earlier. Shares closed about 5% lower. "
                    "Amer, which also owns Arc’teryx, Salomon, and a number of other athletic equipment and "
                    "apparel brands, operates in three distinct business segments. They are technical apparel, "
                    "which includes its pricey Arc’teryx winter jackets; outdoor performance, such as Salomon’s "
                    "winter sports equipment; and ball and racquet sports, which includes equipment and apparel "
                    "from Wilson and Louisville, among others.  During the quarter, sales for Amer’s technical "
                    "apparel rose 26% year over year to $550 million, driven by a 42% jump in direct sales. "
                    "Sales in the segment primarily come from shoppers who are buying directly from Amer’s "
                    "brands rather than from wholesale partners. Sales for outdoor performance increased 2% to "
                    "$523 million, driven by strength in the segment’s winter sports equipment franchise, "
                    "which was offset by a slowdown in wholesale orders for Salomon footwear. Ball and racquet sales "
                    "declined 3% to $242 million as the segment lapped tougher comps. In the year-ago period, "
                    "retailers were still dealing with supply chain issues and had over-ordered equipment like "
                    "tennis rackets and baseball bats. As they looked to keep their inventory levels in check, "
                    "some wholesalers pulled back on orders during the quarter, but Amer expects the segment "
                    "will level out in the quarters ahead and end fiscal 2024 with sales up in the low- to "
                    "mid-single digit range. The company started trading on the New York Stock Exchange last "
                    "month under the ticker “AS.” The shares rose just 3% in Amer’s debut on the public "
                    "markets after it priced its IPO at a discount. Sellers showed muted interest in the "
                    "stock during its first day of trading over concerns about its connections and exposure to "
                    "China and its debt-laden balance sheet. Founded in Helsinki in 1950, Amer was a Finnish public "
                    "company until it was taken private in 2019 by a consortium of investors led by China’s Anta "
                    "Sports, FountainVest Partners, Anamered Investments and Tencent. Since the acquisition, "
                    "sales grew about 45% from $2.45 billion in 2020 to $3.55 billion in 2022. Revenue jumped "
                    "again in 2023 to $4.37 billion, the company said Tuesday."},

        {
            "context": "Shares of Dell Technologies popped more than 15% during extended trading Thursday after the company "
                       "released fourth-quarter results that beat analysts’ estimates and showed strong demand for its "
                       "artificial intelligence servers. Here’s how the company did: Earnings per share: $2.20 adjusted vs. "
                       "$1.73 expected by LSEG, formerly known as Refinitiv Revenue: $22.32 billion vs. $22.16 billion "
                       "expected by LSEG Dell’s revenue for the fiscal 2024 fourth quarter fell 11% from $25.04 billion "
                       "in the year-ago quarter. The company reported net income $1.16 billion, up 89% from the $614 million "
                       "it posted in the same period last year. Chief Financial Officer Yvonne McGill said in a release "
                       "that the company is increasing its annual dividend by 20% to $1.78 per share, which she called "
                       "a “testament to our confidence in the business.” Dell’s Infrastructure Solutions Group (ISG) "
                       "reported $9.3 billion in revenue for the quarter, down 6% year over year but up 10% from the "
                       "third quarter. Servers and networking revenue made up the bulk of that, with $4.9 billion in "
                       "revenue driven by “AI-optimized servers.” Storage revenue came in at $4.5 billion. The company’s "
                       "Client Solutions Group (CSG) reported $11.7 billion for the quarter, down 12% year over year. "
                       "That includes $9.6 billion in commercial client revenue, which fell 11% since the fourth quarter "
                       "of last year, and $2.2 billion in consumer revenue, down 19% year over year. “Our strong AI-optimized "
                       "server momentum continues, with orders increasing nearly 40% sequentially and backlog nearly "
                       "doubling, exiting our fiscal year at $2.9 billion,” Chief Operating Officer Jeff Clarke "
                       "said in the release. For its first quarter, Dell said during its quarterly call with "
                       "investors that it expects to report revenue between $21 billion and $22 billion. The company "
                       "said it is encouraged by momentum around AI, and that it expects to return to growth for "
                       "fiscal 2025. However, the company noted that the macroeconomic environment is causing some "
                       "customers to be cautious about infrastructure costs."},

        {"context": "Birkenstock on Thursday beat holiday quarter revenue expectations, reporting a 22% year-on-year "
                    "jump, as the German sandal company benefited from higher pricing and rising U.S. demand. As a newly "
                    "public company, Birkenstock is still getting into a public reporting rhythm and only just "
                    "released its fiscal 2023 results and 2024 guidance a little over a month ago. On Thursday, "
                    "it said it stands by guidance issued then and still expects sales to be between 1.74 billion "
                    "euros and 1.76 billion euros ($1.89 billion and $1.91 billion), representing growth of 17% to 18%. "
                    "The shoemaker, which started trading on the New York Stock Exchange under the ticker “BIRK” in "
                    "October, saw a muted debut when it first hit the public markets, with shares sliding more than "
                    "12% on its first day as a public company. The stock has since rebounded and is up more than 5% "
                    "this year, as of the Wednesday close. Birkenstock’s shares closed more than 2% lower Thursday.  "
                    "Here’s how the shoemaker did in its fiscal first quarter compared with what Wall Street was "
                    "anticipating, based on a survey of analysts by LSEG, formerly known as Refinitiv: Earnings per "
                    "share: 9 euro cents adjusted vs. 9 euro cents expected.  Revenue: 302.9 million euros vs. 288.7 "
                    "million euros expected. The company reported a net loss of 7.15 million euros for the "
                    "three-month period that ended Dec. 31, or a loss of 4 euro cents per share. A year earlier, "
                    "it reported a loss of 9.19 million euros, or a loss of 5 euro cents per share. "
                    "Excluding one-time items, Birkenstock reported a profit of 17 million euros, or "
                    "9 euro cents per share.  Sales rose to 302.9 million euros, up 22% from 248.5 million euros "
                    "a year earlier. Adjusted earnings before interest, taxation, depreciation and amortization "
                    "(EBITDA) rose 12% year on year to 81 million euros, with an adjusted EBITDA margin of 26.9%, "
                    "down from 29.1% a year earlier. The retailer has been making strides to grow its direct-to-consumer "
                    "business, which comes with better profits and more customer insights than relying on wholesale partners. "
                    "CEO Oliver Reichert has said the company deliberately engineers its distribution strategy so "
                    "demand is higher than supply but it’s working to double its production capabilities over "
                    "the next three years to narrow that gap. The chief executive said those investments, "
                    "along with other efforts the company is undertaking to drive growth, is having a “planned” "
                    "but “temporary” impact to profitability. The company’s gross profit margin inched down to "
                    "61% from 61.7% during the same period last year, with Birkenstock citing “unfavorable "
                    "currency translation and the planned, temporary under-absorption from our ongoing "
                    "capacity expansion.” The company said it continues to carefully track input costs and "
                    "is mitigating inflationary pressures with “executed, selective price increases.” In Europe, the "
                    "company said it had “two consecutive price adjustments” with “no signs of rejection.”"},

        {"context": "Best Buy surpassed Wall Street’s revenue and earnings expectations for the holiday quarter on "
                    "Thursday, even as the company navigated through a period of tepid consumer electronics demand.  "
                    "But the retailer warned of another year of softer sales and said it would lay off workers and "
                    "cut other costs across the business. CEO Corie Barry offered few specifics, but said the "
                    "company has to make sure its workforce and stores match customers’ changing shopping habits. "
                    "Cuts will free up capital to invest back into the business and in newer areas, such as artificial "
                    "intelligence, she added. “This is giving us some of that space to be able to reinvest into "
                    "our future and make sure we feel like we are really well positioned for the industry to "
                    "start to rebound,” she said on a call with reporters. For this fiscal year, Best Buy anticipates "
                    "revenue will range from $41.3 billion to $42.6 billion. That would mark a drop from the most "
                    "recently ended fiscal year, when full-year revenue totaled $43.45 billion. It said comparable "
                    "sales will range from flat to a 3% decline. The retailer plans to close 10 to 15 stores "
                    "this year after shuttering 24 in the past fiscal year. One challenge that will affect sales "
                    "in the year ahead: it is a week shorter. Best Buy said the extra week in the past fiscal "
                    "year lifted revenue by about $735 million and boosted diluted earnings per share by about "
                    "30 cents. Shares of Best Buy closed more than 1% higher Thursday after briefly touching "
                    "a 52-week high of $86.11 earlier in the session. Here’s what the consumer electronics "
                    "retailer reported for its fiscal fourth quarter of 2024 compared with what Wall Street was "
                    "expecting, based on a survey of analysts by LSEG, formerly known as Refinitiv: "
                    "Earnings per share: $2.72, adjusted vs. $2.52 expected Revenue: $14.65 billion vs. $14.56 "
                    "billion expected A dip in demand, but a better-than-feared holiday Best Buy has dealt "
                    "with slower demand in part due to the strength of its sales during the pandemic. Like "
                    "home improvement companies, Best Buy saw outsized spending as shoppers were stuck at "
                    "home. Plus, many items that the retailer sells like laptops, refrigerators and home "
                    "theater systems tend to be pricier and less frequent purchases. The retailer has cited other "
                    "challenges, too: Shoppers have been choosier about making big purchases while dealing "
                    "with inflation-driven higher prices of food and more. Plus, they’ve returned to "
                    "splitting their dollars between services and goods after pandemic years of little "
                    "activity. Even so, Best Buy put up a holiday quarter that was better than feared. "
                    "In the three-month period that ended Feb. 3, the company’s net income fell by 7% to "
                    "$460 million, or $2.12 per share, from $495 million, or $2.23 per share in the year-ago "
                    "period. Revenue dropped from $14.74 billion a year earlier. Comparable sales, a metric that "
                    "includes sales online and at stores open at least 14 months, declined 4.8% during the "
                    "quarter as shoppers bought fewer appliances, mobile phones, tablets and home theater "
                    "setups than the year-ago period. Gaming, on the other hand, was a strong sales "
                    "category in the holiday quarter."}

    ]

    return earnings_releases


def hello_world_test(test_set, qa_model="slim-qa-gen-tiny-tool", question_type="question", temperature=0.5):

    """ Shows a basic example of generating questions and answers from a test set, and then builds a simple mini
    illustrative 'model-ready' instruct database built without any manual labeling or tagging.

        -- test_set = list of dictionary entries with a single key "context" associated with the text passage
        in each test entry

        -- qa_model = name of the qa gen model selected

        -- question_type = "question" | "boolean" | "multiple choice"

        -- temperature = experiment with different levels to optimize balance and variety

    """

    #   recommend using temperature of 0.2 - 0.8 - for multiple choice, use lower end of the range

    #   note: if generation is very long (e.g., a summary question), then it is possible that the
    #   output will be malformed given the cut-off at 500 tokens - in this case, an automated remediation
    #   will try to resolve, but in many cases will provide an empty [] response - we have also observed
    #   some repetition in very long generations too

    qa_model = ModelCatalog().load_model(qa_model, sample=True, temperature=temperature, max_output=500,
                                         get_logits=False)

    qa_pair_set = []
    ds = []

    print(f"\nRun Q-A Gen Inferences on Test Set")

    for text_passage in test_set:

        response = qa_model.function_call(text_passage["context"], params=[question_type], get_logits=False)

        # expect response in the form of:
        #   -- "llm_response": {'question': ['generated question?'], 'answer': ['answer to question']}

        if response:
            if "llm_response" in response:
                if "question" in response["llm_response"] and "answer" in response["llm_response"]:

                    #   get the question and answer from the llm response
                    new_q = response["llm_response"]["question"]
                    new_a = response["llm_response"]["answer"]

                    #   keep only where there is both a non-empty question and answer
                    if new_q and new_a:
                        qa_pair_set.append({"question": new_q[0], "answer": new_a[0]})
                        ds.append(({"question": new_q[0], "answer": new_a[0], "context": text_passage["context"]}))

        print(f"inference - response: ", response)

    print("\nShow list of question-answer pairs created")

    for i, qa_pair in enumerate(qa_pair_set):

        print(f"new generated question-answer pairs: {i} - {qa_pair}")

    print("\nBuild model-ready 'mini' instruct dataset")

    #   use phi-3 instruct wrapper template as separators between elements
    #   --easy to substitute these separators for other popular templates
    sep1= "<|user|>\n"
    sep2 = "<|end|>\n"
    sep3 = "<|assistant|>\n"

    model_ready_ds = []
    for i, sample in enumerate(ds):
        new_sample = sep1 + sample["context"] + "\n" + sample["question"] + sep2 + sep3 + sample["answer"]
        model_ready_ds.append({"text": new_sample, "source": "earnings_test_set_example"})

    random.shuffle(model_ready_ds)
    fp = os.path.join(LLMWareConfig().get_llmware_path(), "instruct_ds_example.jsonl")

    train_file = open(fp, "w")
    for rows in model_ready_ds:
        jsonl_row = json.dumps(rows)
        train_file.write(jsonl_row)
        train_file.write("\n")

    train_file.close()

    print(f"\ncreated dataset @: {fp}")

    return qa_pair_set


if __name__ == "__main__":

    #   get the earnings release test set (list of dicts with "context" key)
    test_set = earning_releases_test_set()

    #   set a max generation on the GGUF engine at 1000 tokens - each model can be loaded up to this amount
    GGUFConfigs().set_config("max_output_tokens", 1000)

    #   run the main example
    hello_world_test(test_set,qa_model="slim-qa-gen-tiny-tool",question_type="question", temperature=0.5)

