import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import { CodeBlock } from "react-code-blocks";

export default function BasicAccordion() {
  const code = `
  import backtrader as bt

  class Strategy(bt.Strategy):
      params = (
          ("short_period", 50),
          ("long_period", 200),
      )
  
      def __init__(self):
          self.short_ma = bt.indicators.SimpleMovingAverage(
              self.data.close, period=self.params.short_period
          )
          self.long_ma = bt.indicators.SimpleMovingAverage(
              self.data.close, period=self.params.long_period
          )
  
      def next(self):
          if self.short_ma > self.long_ma and not self.position:
              # Generate a buy signal and execute the order
              self.buy()
          elif self.short_ma < self.long_ma and self.position:
              # Generate a sell signal and execute the order
              self.sell()
  `;

  return (
    <div>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography>
            Trading Strategy Code
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <CodeBlock
            text={code}
            language='python'
            showLineNumbers={true}
          />
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
