from sqlalchemy import (Column, DateTime, Integer,
                        Sequence, String, Unicode, UnicodeText,
                        )
from sqlalchemy.sql import case
from sqlalchemy.ext.hybrid import hybrid_property
from model_types import Base

# Addresses - used for billing addr, user home addr, (future) recip addr, etc.
class Address(Base):
    __tablename__ = 'addresses'
    public_fields = ['addr_id', 'address', 'city', 'state', 'postal_code', 'country']
    repr_fields = ['address', 'country']

    addr_id = Column(Integer, Sequence('addr_id_seq'), primary_key=True)

    when_updated = Column(DateTime)

    # multi-line entry for street, apartment, c/o, box, whatever other fields you need
    address = Column(UnicodeText)

    # city (usually applicable)
    city = Column(Unicode(200))

    # state, if applicable - if USA, should be a 2-character state abbrev
    state = Column(Unicode(200))

    # _postal_code_city (usually applicable, derived from postal code)
    _postal_code_city = Column('postal_code_city', UnicodeText)

    # _postal_code_state (if applicable derived from postal code, if USA,
    # should be a 2-character state abbrev)
    _postal_code_state = Column('postal_code_state', Unicode(200))

    # zip / postal code, if applicable
    postal_code = Column(Unicode(20))

    # country - should be a 2-character country abbrev, not optional, always ASCII
    country = Column(String(2), nullable=False)

    @property
    def formatted_string(self):
        # UK addresss put a comma before the postal code.
        # Hurting for a library to do this
        if self.country == 'GB':
            lines = [l for l in [self.address, self.city,
                                 self.state, self.postal_code] if l is not None]
            return ', '.join(lines)

        lines = [l for l in [self.address,
                             self.city, self.state] if l is not None]
        if self.postal_code is not None:
            return "{} {}".format(', '.join(lines), self.postal_code)
        else:
            return ', '.join(lines)

    @hybrid_property
    def postal_code_state(self):
        """
        Where available, use the state inferred from postal code for reporting.
        If not available, use user-reported state.
        """
        return self._postal_code_state or self.state

    @postal_code_state.expression  # type: ignore
    def postal_code_state(cls):
        return case([
            (cls._postal_code_state != None, cls._postal_code_state)], else_ = cls.state)

    @postal_code_state.setter # type: ignore
    def postal_code_state(self, postal_code_state):
        self._postal_code_state = postal_code_state

    @hybrid_property
    def postal_code_city(self):
        """
        Where available, use the city inferred from postal code for reporting.
        If not available, use user-reported city.
        """
        return self._postal_code_city or self.city

    @postal_code_city.expression  # type: ignore
    def postal_code_city(cls):
        return case([
            (cls._postal_code_city != None, cls._postal_code_city)], else_ = cls.city)

    @postal_code_city.setter # type: ignore
    def postal_code_city(self, postal_code_city):
        self._postal_code_city = postal_code_city
