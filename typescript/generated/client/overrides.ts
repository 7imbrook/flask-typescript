// Generated file
// To regenereate run flask generate-typescript

// Imports here
import { CustomResponse, ExampleType, LengthResponse } from 'generated/interfaces/example/app/types';
import { SimpleID } from 'generated/interfaces/example/schema/types';
import { IndexRequest } from 'generated/request/IndexRequest';
import { NamingSecondRequest } from 'generated/request/NamingSecondRequest';
import { NumberRequest } from 'generated/request/NumberRequest';
import { ParamsRequest } from 'generated/request/ParamsRequest';
import { PostRequest } from 'generated/request/PostRequest';
import { QueryRequest } from 'generated/request/QueryRequest';

export type APIUrl = "/" | "/<int:custom_id>" | "/naming" | "/number" | "/post" | "/via_query";
export type APIRequest = IndexRequest | NamingSecondRequest | NumberRequest | ParamsRequest | PostRequest | QueryRequest;
export type APIResponse = CustomResponse | ExampleType | LengthResponse | SimpleID;