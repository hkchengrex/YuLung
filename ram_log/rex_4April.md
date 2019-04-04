TODO:
- Build new expansion (done)
- Don't do suicidal scouting
- Make generic unit consistency across frames (Done)
- Scout observation (partly done)

- Oh I just missed some mineral types that's why it doesn't work
- Fixed expansion location checking in Abiogenesis

- Can build new expansion in lower left corner... But it somehow does not refresh 
expansion list

- Fixed a bug in get_all when list of unit types are used

- *NOW* I know why I cannot build two bases. In the loop, I reached, at the same time,
the amount the minerals required to build one of the hatcheries. But then I thought
I can build both at the same time without realizing I can only build one. And 
thus I kicked both out of the queue.
- Solution: early return!

- Use on_going_action to avoid randomly picking a drone with mission to do

- Need inverse lookup on SC2 id <-> our ids