# collection-ai
AI Process to Identify Collection



## Process
- clean up transactions focusing on repayments
- repayments need to be 'anomalous' by the following criteria
    - late (exceed existing date patterns for repayment)
    - substantially less than normal % of outstanding balance
- once a transaction set has been determined to be in error
    - identify a "minimum" value to set as a new repayment offer
    - "minimum" should exceed the minimum payment to contribute to capital paydown
    - "minimum" should fit within regular payment cycles
- build a plan using an LLM to repay even 'smaller' amounts more often
- add verbiage around repayment structures
- repeat to observe