# Reflection draft (rewrite in your own words before you submit)

**What I built.** A screener that takes a pasted internship or job posting and says Good fit, Check carefully or Risky, with the rules that triggered the label.

**What I changed from my first idea.** I first planned a platform that collects postings from Internshala, LinkedIn and Naukri. Those sites' terms don't allow scraping, so I narrowed it to a tool where the user pastes a posting. That gave me something I could finish and test honestly.

**What went wrong first.** My first rules looked for fees and deposits. On 29 real postings they scored 34%, worse than guessing, and caught 0 of 9 risky postings. None of the risky ones asked for a fee. The real warning signs were unpaid roles promising big salaries later, claims of thousands of people hired, "comment INTERESTED" posts and training companies.

**What I learned.** Testing on real data showed my assumption was wrong, and I would not have found that from the sample data I made up first. I also learned that a score on the same data I used to write the rules is too optimistic, so I say so in the README.

**What I would do next.** Test on postings the rules have never seen, collect more Good fit postings, and let users report wrong verdicts.

**How I used AI.** I used Claude to help write and test the code and to draft the first labels. I reviewed the labels and the results myself. (Edit this line so it is true for you.)
