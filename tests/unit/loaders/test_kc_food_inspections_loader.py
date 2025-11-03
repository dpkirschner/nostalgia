import csv
import json
from datetime import date
from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.kc_food_inspection import KcFoodInspection


class TestKcFoodInspectionsLoader:
    @pytest.fixture
    def sample_csv_valid(self):
        return StringIO(
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"STARBUCKS","123 MAIN ST","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"SUBWAY","456 PIKE ST","SEATTLE","WA","98102","-122.3400","47.6100","03/24/2025"\n'
        )

    @pytest.fixture
    def sample_csv_with_defaults(self):
        return StringIO(
            '"Name","Address","City","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"TACO BELL","789 BROADWAY","SEATTLE","98103","-122.3500","47.6200","11/18/2024"\n'
        )

    @pytest.fixture
    def sample_csv_missing_required(self):
        return StringIO(
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"","123 MAIN ST","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"BURGER KING","","SEATTLE","WA","98102","-122.3400","47.6100","03/24/2025"\n'
            '"MCDONALDS","999 PINE ST","SEATTLE","WA","98103","","","01/01/2025"\n'
        )

    @pytest.fixture
    def sample_csv_date_formats(self):
        return StringIO(
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"CAFE A","100 1ST AVE","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"CAFE B","200 2ND AVE","SEATTLE","WA","98102","-122.3400","47.6100","2025-03-24"\n'
            '"CAFE C","300 3RD AVE","SEATTLE","WA","98103","-122.3500","47.6200","invalid-date"\n'
            '"CAFE D","400 4TH AVE","SEATTLE","WA","98104","-122.3600","47.6300",""\n'
        )

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.add_all = MagicMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def mock_async_session_local(self, mock_session):
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        return mock_context

    async def test_load_valid_csv_data(self, tmp_path, mock_async_session_local, mock_session):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"STARBUCKS","123 MAIN ST","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        assert mock_session.add_all.called
        added_inspections = mock_session.add_all.call_args[0][0]
        assert len(added_inspections) == 1

        inspection = added_inspections[0]
        assert isinstance(inspection, KcFoodInspection)
        assert inspection.business_name == "STARBUCKS"
        assert inspection.address == "123 MAIN ST"
        assert inspection.city == "SEATTLE"
        assert inspection.state == "WA"
        assert inspection.zip == "98101"
        assert inspection.latitude == -122.3321
        assert inspection.longitude == 47.6062
        assert inspection.inspection_date == date(2025, 8, 15)

        raw_data = json.loads(inspection.raw_line)
        assert raw_data["Name"] == "STARBUCKS"

    async def test_load_defaults_state_to_wa(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"TACO BELL","789 BROADWAY","SEATTLE","98103","-122.3500","47.6200","11/18/2024"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        added_inspections = mock_session.add_all.call_args[0][0]
        assert len(added_inspections) == 1
        assert added_inspections[0].state == "WA"

    async def test_skips_rows_with_missing_business_name(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"","123 MAIN ST","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"   ","456 PIKE ST","SEATTLE","WA","98102","-122.3400","47.6100","03/24/2025"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        if mock_session.add_all.called:
            added_inspections = mock_session.add_all.call_args[0][0]
            assert len(added_inspections) == 0

    async def test_skips_rows_with_missing_address(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"BURGER KING","","SEATTLE","WA","98102","-122.3400","47.6100","03/24/2025"\n'
            '"MCDONALDS","   ","SEATTLE","WA","98103","-122.3500","47.6200","01/01/2025"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        if mock_session.add_all.called:
            added_inspections = mock_session.add_all.call_args[0][0]
            assert len(added_inspections) == 0

    async def test_skips_rows_with_missing_coordinates(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"RESTAURANT A","100 1ST AVE","SEATTLE","WA","98101","","-122.3321","08/15/2025"\n'
            '"RESTAURANT B","200 2ND AVE","SEATTLE","WA","98102","-122.3400","","03/24/2025"\n'
            '"RESTAURANT C","300 3RD AVE","SEATTLE","WA","98103","","","01/01/2025"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        if mock_session.add_all.called:
            added_inspections = mock_session.add_all.call_args[0][0]
            assert len(added_inspections) == 0

    async def test_skips_rows_with_invalid_coordinates(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"RESTAURANT A","100 1ST AVE","SEATTLE","WA","98101","invalid","-122.3321","08/15/2025"\n'
            '"RESTAURANT B","200 2ND AVE","SEATTLE","WA","98102","-122.3400","not-a-number","03/24/2025"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        if mock_session.add_all.called:
            added_inspections = mock_session.add_all.call_args[0][0]
            assert len(added_inspections) == 0

    async def test_date_parsing_multiple_formats(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"CAFE A","100 1ST AVE","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"CAFE B","200 2ND AVE","SEATTLE","WA","98102","-122.3400","47.6100","2025-03-24"\n'
            '"CAFE C","300 3RD AVE","SEATTLE","WA","98103","-122.3500","47.6200","invalid-date"\n'
            '"CAFE D","400 4TH AVE","SEATTLE","WA","98104","-122.3600","47.6300",""\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        added_inspections = mock_session.add_all.call_args[0][0]
        assert len(added_inspections) == 4

        assert added_inspections[0].inspection_date == date(2025, 8, 15)
        assert added_inspections[1].inspection_date == date(2025, 3, 24)
        assert added_inspections[2].inspection_date is None
        assert added_inspections[3].inspection_date is None

    async def test_stores_raw_csv_as_json(self, tmp_path, mock_async_session_local, mock_session):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date","Extra Field"\n'
            '"PIZZA HUT","555 5TH AVE","SEATTLE","WA","98105","-122.3700","47.6400","12/25/2024","Extra Data"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        added_inspections = mock_session.add_all.call_args[0][0]
        raw_data = json.loads(added_inspections[0].raw_line)

        assert raw_data["Name"] == "PIZZA HUT"
        assert raw_data["Address"] == "555 5TH AVE"
        assert raw_data["Extra Field"] == "Extra Data"

    async def test_batch_processing(self, tmp_path, mock_async_session_local, mock_session):
        rows = [
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"'
        ]
        for i in range(2500):
            rows.append(
                f'"RESTAURANT {i}","{i} MAIN ST","SEATTLE","WA","98101","-122.{3300+i}","47.{6000+i}","01/01/2025"'
            )
        csv_content = "\n".join(rows)

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file), batch_size=1000)

        assert mock_session.add_all.call_count == 3
        assert mock_session.commit.call_count == 3

    async def test_batch_processing_partial_final_batch(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        rows = [
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"'
        ]
        for i in range(1500):
            rows.append(
                f'"RESTAURANT {i}","{i} MAIN ST","SEATTLE","WA","98101","-122.{3300+i}","47.{6000+i}","01/01/2025"'
            )
        csv_content = "\n".join(rows)

        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file), batch_size=1000)

        assert mock_session.add_all.call_count == 2
        assert mock_session.commit.call_count == 2

    async def test_empty_csv_file(self, tmp_path, mock_async_session_local, mock_session):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        assert not mock_session.add_all.called
        assert not mock_session.commit.called

    async def test_mixed_valid_and_invalid_rows(
        self, tmp_path, mock_async_session_local, mock_session
    ):
        csv_content = (
            '"Name","Address","City","State","Zip Code","Latitude","Longitude","Inspection Date"\n'
            '"VALID RESTAURANT","100 MAIN ST","SEATTLE","WA","98101","-122.3321","47.6062","08/15/2025"\n'
            '"","200 PIKE ST","SEATTLE","WA","98102","-122.3400","47.6100","03/24/2025"\n'
            '"ANOTHER VALID","300 BROADWAY","SEATTLE","WA","98103","-122.3500","47.6200","11/18/2024"\n'
            '"INVALID COORDS","400 1ST AVE","SEATTLE","WA","98104","invalid","47.6300","01/01/2025"\n'
            '"THIRD VALID","500 2ND AVE","SEATTLE","WA","98105","-122.3700","47.6400","12/25/2024"\n'
        )
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        with patch(
            "scripts.load_kc_food_inspections.AsyncSessionLocal",
            return_value=mock_async_session_local,
        ):
            from scripts.load_kc_food_inspections import load_kc_food_inspections

            await load_kc_food_inspections(str(csv_file))

        added_inspections = mock_session.add_all.call_args[0][0]
        assert len(added_inspections) == 3
        assert added_inspections[0].business_name == "VALID RESTAURANT"
        assert added_inspections[1].business_name == "ANOTHER VALID"
        assert added_inspections[2].business_name == "THIRD VALID"
