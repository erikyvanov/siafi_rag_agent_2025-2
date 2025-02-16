class PokemonPlace:
    def __init__(
            self,
            name: str,
            region: str,
            generation: int,
            url: str,
            description: str,
            image_src: str
    ):
        self.name = name
        self.region = region
        self.generation = generation
        self.url = url
        self.description = description
        self.image_src = image_src

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'generation': self.generation,
            'region': self.region,
            'url': self.url,
            'description': self.description,
            'image_src': self.image_src
        }

    @staticmethod
    def from_dict(data: dict):
        return PokemonPlace(
            name=data['name'],
            generation=data['generation'],
            region=data['region'],
            url=data['url'],
            description=data['description'],
            image_src=data['image_src']
        )
