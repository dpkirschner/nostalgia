from pydantic import BaseModel, Field, HttpUrl, field_validator


class MemorySubmissionCreate(BaseModel):
    location_id: int = Field(..., gt=0)
    business_name: str = Field(..., min_length=1, max_length=255)
    start_year: int | None = Field(None, ge=1800, le=2100)
    end_year: int | None = Field(None, ge=1800, le=2100)
    note: str | None = Field(None, max_length=2000)
    proof_url: str | None = Field(None, max_length=500)

    @field_validator("proof_url")
    @classmethod
    def validate_proof_url(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("proof_url must start with http:// or https://")
        return v

    @field_validator("end_year")
    @classmethod
    def validate_years(cls, v: int | None, info) -> int | None:
        if v is not None and "start_year" in info.data:
            start_year = info.data["start_year"]
            if start_year is not None and v < start_year:
                raise ValueError("end_year must be >= start_year")
        return v


class MemorySubmissionResponse(BaseModel):
    id: int
    location_id: int
    business_name: str
    status: str
    message: str = "Memory submission received and pending review"
