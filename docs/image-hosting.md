# Image hosting strategy

The alpha site references established external image assets rather than copying binaries into the repository. For Wikimedia Commons, the display URL uses a Commons file redirect while `image_source_url` preserves the human-readable File page containing creator and license metadata.

This reduces duplicate asset management, but the public record must retain source and rights metadata locally so a later hosting change does not erase the provenance chain. A future preservation pass may cache derivatives if licensing, attribution, repository size, and deployment behavior are addressed explicitly.
