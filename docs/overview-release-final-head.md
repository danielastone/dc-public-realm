# Final-head protection

When the pull request is ready, record the exact head SHA that passed CI and supply it as the expected head for merge. Any intervening commit should require a fresh CI result rather than inheriting the earlier green state.
